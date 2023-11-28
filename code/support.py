from os import walk
import pygame

class ResourceLoader:
    '''Interface for resource loaders.'''
    def import_folder(self, path):
        '''Import a folder of images.'''
        pass

    def import_folder_dict(self, path):
        '''Import a folder of images as a dictionary.'''
        pass

class RealResourceLoader(ResourceLoader):
    '''Real resource loader.'''
    def import_folder(self, path):
        '''Import a folder of images.'''
        surface_list = []
        for _, __, img_files in walk(path):
            for image in img_files:
                full_path = path + '/' + image
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surf)
        return surface_list

    def import_folder_dict(self, path):
        '''Import a folder of images as a dictionary.'''
        surface_dict = {}
        for _, __, img_files in walk(path):
            for image in img_files:
                full_path = path + '/' + image
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_dict[image.split('.')[0]] = image_surf
        return surface_dict

class FolderImportProxy(ResourceLoader):
    '''Proxy for resource loader.'''
    def __init__(self):
        '''Initialize the proxy.'''
        self.loader = RealResourceLoader()
        self.cache = {}

    def import_folder(self, path):
        '''Import a folder of images.'''
        if path not in self.cache:
            self.cache[path] = self.loader.import_folder(path)
        return self.cache[path]

    def import_folder_dict(self, path):
        '''Import a folder of images as a dictionary.'''
        if path not in self.cache:
            self.cache[path] = self.loader.import_folder_dict(path)
        return self.cache[path]
