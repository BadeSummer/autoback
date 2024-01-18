LOCAL_CONFIG_SECTION = 'LocalFiles'
BAIDU_CONFIG_SECTION = 'BaiduCloud'

import os
import hashlib
import logging


def get_all_files_in_directory(directory):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:

            # 忽略.DS文件
            if filename.startswith('.DS'):
                continue

            # 忽略缓存的分片文件
            if '_chunk_' in filename:
                continue

            # 拼接完整的文件路径
            full_path = os.path.join(dirpath, filename)

            all_files.append(full_path)
    return all_files


def remove_all_chunks(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # 拼接完整的文件路径
            full_path = os.path.join(dirpath, filename)
            
            if '_chunk_' in full_path:
                os.remove(full_path)


def cal_file_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class File:
    '''
    文件类
    
    Args:
        file_path (str) : 文件路径
    
    Attributes:
        file_path : 
        file_size : 
        file_md5 : 
        chunks : 所有切片，一个列表
    
    Methods:
        needs_chunking() : 
    '''
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.file_md5 = cal_file_md5(self.file_path)
        self.chunks = []  # 切片列表

    def needs_chunking(self, chunk_size):
        # 根据给定的块大小判断文件是否需要切片
        ischunk = self.file_size > chunk_size
        chunk_amount = self.file_size // chunk_size + 1
        return ischunk, chunk_amount
    
    def make_block_list(self):
        logging.debug(f'构建 block_list')

        if not self.chunks :
            logging.debug('切片列表为空')
            raise Exception(f'还未进行预处理')
        self.block_list = []
        for chunk in self.chunks:
            self.block_list.append(chunk.chunk_md5)
        self.block_list = str(self.block_list).replace("'",'"')


    def remove_chunks(self):
        '''删除本地的chunks文件'''
        for chunk in self.chunks:
            os.remove(chunk.chunk_path)
            logging.debug(f'清理缓存{chunk.chunk_path}')

    
class FileChunk:
    '''
    文件切片类
    
    Args:
        chunk_path (str): 
        mother_file (File): 
        partseq (int): 
    
    Attributes:
        chunk_path : 
        mother_file : 
        chunk_index : 
        chunk_md5 : 
    
    '''
    def __init__(self, chunk_path, mother_file, partseq):
        self.chunk_path = chunk_path
        self.mother_file = mother_file
        self.chunk_index = partseq
        self.chunk_md5 = cal_file_md5(chunk_path)



class FilePreprocessor:
    '''
    分片上传预处理器

    Args:
        File (File) : File类
        chunk_size (int) : 切片大小，单位为B 默认为4MB

    Attributes:
        file : 
        chunk_size : 

    Method:
        preprocess() : 
    '''
    def __init__(self, File, chunk_size=4*1024*1024, max_chunk_amount=1024):
        self.file = File
        self.chunk_size = chunk_size
        self.max_chunk_amount = max_chunk_amount

    def preprocess(self):
        logging.debug(f'文件预处理')

        # 确保文件路径中的目录存在
        os.makedirs(os.path.dirname(self.file.file_path), exist_ok=True)

        # 判断文件是否需要切片
        needchunk, chunks_amount = self.file.needs_chunking(self.chunk_size)
        if chunks_amount > self.max_chunk_amount:
            raise f'分片数量超过{ self.max_chunk_amount }'

        self._chunk_file()
        self.file.make_block_list()
            

    def _chunk_file(self):
        # 创建文件切片
        logging.debug(f'切片文件')
        with open(self.file.file_path, 'rb') as f:
            logging.debug(f'读取文件 {self.file.file_path} 准备切片')
            part_seq = 0

            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    logging.debug(f'切片列表中含有{len(self.file.chunks)}个切片')

                    return '切片完成'

                chunk_path = f"{ self.file.file_path }_path_chunk_{ part_seq }"
                with open(chunk_path, 'wb') as cf:
                    logging.debug(f'创建第{part_seq}个切片')
                    cf.write(chunk)
                logging.debug(f'加入第{part_seq}个切片到 chunks')    
                self.file.chunks.append(FileChunk(chunk_path, self.file, part_seq))

                part_seq += 1
