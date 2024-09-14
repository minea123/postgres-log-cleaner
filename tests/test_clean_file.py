import os
import unittest
import random
import shutil
import clean_file

contents = [
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
    "The purpose of our lives is to be happy. - Dalai Lama",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "Get busy living, or get busy dying. - Stephen King",
    "You only live once, but if you do it right, once is enough. - Mae West"
]


class TestCleanFile(unittest.TestCase):
    def setUp(self):
        os.makedirs("./test_dir/empty", exist_ok=True)
        os.makedirs("./test_dir/files", exist_ok=True)
        for i in range(100):
            file_name = f"test{i}.log"
            with open(f"./test_dir/files/{file_name}", 'w') as file:
                file_content = random.choice(contents)
                file.write(file_content)

    def tearDown(self):
        shutil.rmtree("./test_dir/empty")
        shutil.rmtree("./test_dir/files")

    def test_directory_not_exist(self):
        """Test to check in case no directory exist, the function must raise exception """
        not_exist_path = f"./test_dir/fake_not_exist"
        with self.assertRaises(Exception):
            clean_file.clean_file(not_exist_path)

    def test_clean_file(self):
        base_path = "./test_dir/files"
        """Test to check in case directory has 100 files, the function must clean and count file equal 100 
        and size of delete more than 0 """
        file_number, file_size = clean_file.clean_file(base_path)
        self.assertEqual(100, file_number, "total files has been delete must be 100 ")
        self.assertLess(0, file_size, "File size must be greater than 0")
