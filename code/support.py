from os import walk
import pygame

# Resource Loader Interface
class ResourceLoader:
    def import_folder(self, path):
        pass

    def import_folder_dict(self, path):
        pass

# Real Resource Loader
class RealResourceLoader(ResourceLoader):
    def import_folder(self, path):
        surface_list = []
        for _, __, img_files in walk(path):
            for image in img_files:
                full_path = path + '/' + image
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surf)
        return surface_list

    def import_folder_dict(self, path):
        surface_dict = {}
        for _, __, img_files in walk(path):
            for image in img_files:
                full_path = path + '/' + image
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_dict[image.split('.')[0]] = image_surf
        return surface_dict

# Folder Import Proxy
class FolderImportProxy(ResourceLoader):
    def __init__(self):
        self.loader = RealResourceLoader()
        self.cache = {}

    def import_folder(self, path):
        if path not in self.cache:
            self.cache[path] = self.loader.import_folder(path)
        return self.cache[path]

    def import_folder_dict(self, path):
        if path not in self.cache:
            self.cache[path] = self.loader.import_folder_dict(path)
        return self.cache[path]
