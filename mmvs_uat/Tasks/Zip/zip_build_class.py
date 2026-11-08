import zipfile
import io
from pathlib import Path
import time
from typing import List, Optional, Tuple, Dict
from ... import bpl
from ... import config
from ..Base.build_task_base import BuildTaskBase

# File extensions that are already compressed by Unreal's cooker: recompressing them with
# DEFLATE wastes CPU time for no size benefit, so they are stored as-is in the zip instead.
ALREADY_COMPRESSED_EXTENSIONS = {".pak", ".ucas", ".utoc"}


        

        
class RawZipBuilder(BuildTaskBase):
    def __init__(self):
        super().__init__()

        # List of paths to include in the zip
        # Each entry is (root folder in the zip, Path to include, optional list of file name prefixes to filter on)
        # Use "" to include at the root of the zip. Use None filters to include every file in the folder.
        self.folder_paths_to_include: List[Tuple[str, Path, Optional[List[str]]]] = []
        self.zip_destination_file: Path = Path()

        self.total_files: int = 0
        self.files_processed: int = 0

        if config:
            self.zip_files_inside_ram: bool = config.zip_files_inside_ram
            self.zip_compression = config.zip_compression
            self.zip_compression_level = config.zip_compression_level
        else:
            self.zip_files_inside_ram: bool = True
            self.zip_compression = zipfile.ZIP_DEFLATED
            self.zip_compression_level = 6

    def send_stop_request(self) -> None:
        self.cancel_requested = True

    def current_progress_factor(self) -> float:
        """Returns the current progress of the zip build."""
        if self.start_time < 0.0:
            return 0.0
        elif self.end_time >= 0.0:
            return 1.0
        else:
            return self.files_processed / self.total_files if self.total_files > 0 else 0.0

    def get_current_progress_text(self, colored: bool = True) -> str:
        if self.start_time < 0.0:
            return "Not started."
        elif self.end_time >= 0.0:
            if self.cancel_requested:
                if colored:
                    return bpl.color_set.red("Canceled!")
                return "Canceled!"
            if self.success:
                if colored:
                    text = bpl.color_set.green("Successfully!")
                else:
                    text = f"Successfully!"
                text += f" Done in {bpl.utils.get_formatted_time(self.end_time - self.start_time)}"
                text += f" {self.files_processed}/{self.total_files} files processed."
                return text
            else:
                if colored:
                    return bpl.color_set.red("Failed!")
                return "Failed!"
        else:
            # Check if all files have been processed
            if self.total_files > 0 and self.files_processed >= self.total_files:
                # Files processing is complete, show as complete but still finalize ZIP
                if colored:
                    text = bpl.color_set.yellow("In progress...")
                else:
                    text = "In progress..."
                text += f" {self.files_processed}/{self.total_files} files processed. 100.00% complete"
                return text
            else:
                if colored:
                    text = bpl.color_set.yellow("In progress...")
                else:
                    text = "In progress..."
                text += f" {self.files_processed}/{self.total_files} files processed."
                percent_complete = (self.files_processed / self.total_files) * 100 if self.total_files > 0 else 0
                text += f" {percent_complete:.2f}% complete"
                return text
        
    def get_build_finished(self) -> bool:
        """
        Check if the build has finished.
        Returns True if the build is finished (either success or failure), False otherwise.
        """
        return self.start_time != -1.0 and self.end_time != -1.0

    def update_progress(self, file_path: Path) -> None:
        """Updates and displays the progress percentage."""
        self.files_processed += 1
        percent_complete = (self.files_processed / self.total_files) * 100 if self.total_files > 0 else 0
        self.print_log(f"Processing {file_path}: {percent_complete:.2f}% complete")

    @staticmethod
    def count_files(directory: Path, name_filters: Optional[List[str]] = None) -> int:
        """Counts the total number of files in the directory and its subdirectories, optionally filtered by name prefixes."""
        return sum(1 for f in directory.rglob('*') if f.is_file() and RawZipBuilder._file_matches_filters(f, name_filters))

    @staticmethod
    def _file_matches_filters(file_path: Path, name_filters: Optional[List[str]]) -> bool:
        if not name_filters:
            return True
        return any(file_path.name.startswith(name_filter) for name_filter in name_filters)

    def _get_compress_type_for_file(self, file_path: Path) -> int:
        """Returns ZIP_STORED for already-compressed files, the configured compression otherwise."""
        if file_path.suffix.lower() in ALREADY_COMPRESSED_EXTENSIONS:
            return zipfile.ZIP_STORED
        return self.zip_compression

    # PLEASE REPLACE OS.PATH BY PATHLIB WHERE POSSIBLE
    def preload_files_in_memory(self, folder_paths: List[Tuple[str, Path, Optional[List[str]]]]) -> Optional[List[Tuple[Path, bytes, int]]]:
        files_in_memory: Dict[Path, Tuple[bytes, int]] = {}
        success = True
        for root_folder, folder_path, name_filters in folder_paths:
            for file_path in folder_path.rglob('*'):
                if self.cancel_requested:
                    return None
                if file_path.is_file() and self._file_matches_filters(file_path, name_filters):
                    arcname = file_path.relative_to(folder_path)
                    if root_folder:
                        arcname = Path(root_folder) / arcname
                    if arcname not in files_in_memory:
                        try:
                            with open(file_path, 'rb') as f:
                                data = f.read()
                                files_in_memory[arcname] = (data, self._get_compress_type_for_file(file_path))
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
                            success = False
                    else:
                        print(f"File {arcname} is already in memory, it will be ignored.")
                        success = False
        if success:
            # Returns a list of tuples (arcname, data, compress_type)
            return [(arcname, data, compress_type) for arcname, (data, compress_type) in files_in_memory.items()]
        else:
            print("Error during file preloading in memory.")
            return None

    def add_folder_to_zip(self, zip_file: zipfile.ZipFile, root_folder: str, folder_path: Path, name_filters: Optional[List[str]] = None) -> bool:
        """Adds a folder to the ZIP file with a callback function for progress."""
        if self.cancel_requested:
            return False

        for file_path in folder_path.rglob('*'):
            if self.cancel_requested:
                return False
            if file_path.is_file() and self._file_matches_filters(file_path, name_filters):
                arcname = file_path.relative_to(folder_path)
                if root_folder:
                    arcname = Path(root_folder) / arcname
                zip_file.write(file_path, arcname, compress_type=self._get_compress_type_for_file(file_path))
                self.update_progress(file_path)  # Call callback function to update progress
        return True

    @staticmethod
    def _cleanup_temp_file(temp_path: Path) -> None:
        """Removes a leftover temporary zip file after a failed or canceled build."""
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception as error:
            print(bpl.color_set.red(f"Failed to remove temporary zip file {temp_path}: {error}"))

    def create_build_zip(self) -> bool:
        if self.cancel_requested:
            return False

        # Check
        if len(self.folder_paths_to_include) == 0:
            print("No folders to add to ZIP. Please check the provided paths.")
            print("Provided folder paths:")
            for root_folder, path, _ in self.folder_paths_to_include:
                print(bpl.color_set.red(f"Root folder in ZIP: '{root_folder}', Path to include: '{path}'"))
            self.success = False
            return False
        for _, path, _ in self.folder_paths_to_include:
            if not path.exists():
                if not config.fake_build_and_zip:
                    print(bpl.color_set.red(f"Path {path} does not exist. Please check the provided paths."))
                    self.success = False
                    return False
            else:
                # Check if zip destination is not in the f9
                #older paths
                try:
                    if self.zip_destination_file.resolve().is_relative_to(path.resolve()):
                        print(bpl.color_set.red(f"ZIP destination file {self.zip_destination_file} cannot be within source folders."))
                        self.success = False
                        return False
                except ValueError:
                    pass
        if not self.zip_destination_file:
            print(bpl.color_set.red("No ZIP destination file specified. Please check the configuration."))
            self.success = False
            return False

        # Write to a temporary file first, then atomically rename it, so the final destination
        # never ends up with a partial/corrupted zip if the process is canceled or crashes.
        temp_destination = self.zip_destination_file.with_name(self.zip_destination_file.name + ".tmp")

        # ZIP preparation
        self.print_log("Prepare ZIP...")
        self.start_time = time.time()
        counter = bpl.utils.CounterTimer()

        # Calculate total number of files
        self.total_files = 0
        for _, path, name_filters in self.folder_paths_to_include:
            self.total_files += self.count_files(path, name_filters)
        self.files_processed = 0
        self.print_log("Prepare done in: ", counter.get_str_time())

        self.print_log("Starting ZIP file creation...")
        counter = bpl.utils.CounterTimer()

        if not config.fake_build_and_zip:
            if self.zip_files_inside_ram:
                # Creating ZIP in RAM
                self.print_log("Creating ZIP in RAM...")
                preload_counter = bpl.utils.CounterTimer()
                files_data = self.preload_files_in_memory(self.folder_paths_to_include)
                self.print_log(f"File preloading in memory completed in: {preload_counter.get_str_time()}")
                if files_data:
                    mem_zip = io.BytesIO()
                    zip_file_counter = bpl.utils.CounterTimer()
                    with zipfile.ZipFile(mem_zip, 'w', compression=self.zip_compression, compresslevel=self.zip_compression_level) as zip_file:
                        # Add all files only once
                        for arcname, data, compress_type in files_data:
                            if self.cancel_requested:
                                self.end_time = time.time()
                                self.success = False
                                return False
                            zip_file.writestr(str(arcname), data, compress_type=compress_type)
                            self.update_progress(arcname)
                    self.print_log(f"ZIP created in RAM in: {zip_file_counter.get_str_time()}")
                    
                    # Check if cancellation was requested before writing to disk
                    if self.cancel_requested:
                        self.end_time = time.time()
                        self.success = False
                        return False
                    
                    # Writing ZIP to a temp file on disk all at once, then renaming it atomically
                    save_zip_counter = bpl.utils.CounterTimer()
                    self.print_log("ZIP creation in RAM completed, writing to disk...")
                    with open(temp_destination, 'wb') as f:
                        f.write(mem_zip.getvalue())
                    temp_destination.replace(self.zip_destination_file)
                    self.print_log(f"ZIP written to disk in: {save_zip_counter.get_str_time()}")
                    
                    # All files processed - mark as done for display purposes
                    # IMPORTANT: Set success BEFORE end_time to avoid race condition in parallel mode
                    # MUST be done AFTER file is written to disk!
                    self.success = True
                    self.end_time = time.time()
                else:
                    print(bpl.color_set.red("Error during file preloading in memory."))
                    self.end_time = time.time()
                    self.success = False
                    return False
            else:
                # Creating ZIP directly on disk, into a temp file so the final destination is only
                # ever touched once the archive is fully and successfully written.
                with zipfile.ZipFile(temp_destination, 'w', compression=self.zip_compression, compresslevel=self.zip_compression_level) as zip_file:
                    for root_folder, path, name_filters in self.folder_paths_to_include:
                        if self.cancel_requested:
                            zip_file.close()
                            self._cleanup_temp_file(temp_destination)
                            self.end_time = time.time()
                            self.success = False
                            return False
                        zip_folder_counter = bpl.utils.CounterTimer()
                        result = self.add_folder_to_zip(zip_file, root_folder, path, name_filters)
                        if not result:
                            print(bpl.color_set.red(f"Error adding folder {path} to ZIP."))
                            zip_file.close()
                            self._cleanup_temp_file(temp_destination)
                            self.end_time = time.time()
                            self.success = False
                            return False
                        self.print_log(f"Folder added to ZIP in: {zip_folder_counter.get_str_time()}")
                # ZipFile context manager exits here - all data is flushed to disk
                temp_destination.replace(self.zip_destination_file)
                
                # All files processed - mark as done
                # IMPORTANT: Set success BEFORE end_time to avoid race condition in parallel mode
                # MUST be done AFTER ZipFile is closed and fully written to disk!
                self.success = True
                self.end_time = time.time()
        else:
            self.print_log("Fake zip...")
            time.sleep(config.fake_zip_time_seconds)  # Simulate build time
            self.end_time = time.time()
            self.success = True

        self.print_log("ZIP file created successfully! Elapsed time: " + counter.get_str_time())

        return self.success
