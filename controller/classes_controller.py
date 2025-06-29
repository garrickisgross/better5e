from repos.classes import ClassRepo, SubclassRepo
from models.classes import Class, Subclass

class ClassesController:
    @staticmethod
    def create_class(class_data: dict) -> int:
        class_instance = Class(**class_data)
        return ClassRepo.create(class_instance)

    @staticmethod
    def get_class(class_id: int) -> Class:
        return ClassRepo.get(class_id)

    @staticmethod
    def list_classes() -> list[Class]:
        return ClassRepo.list_all()

    @staticmethod
    def update_class(class_id: int, updates: dict) -> None:
        ClassRepo.update(class_id, updates)

    @staticmethod
    def delete_class(class_id: int) -> None:
        ClassRepo.delete(class_id)

class SubclassesController:
    @staticmethod
    def create_subclass(subclass_data: dict) -> int:
        subclass_instance = Subclass(**subclass_data)
        return SubclassRepo.create(subclass_instance)

    @staticmethod
    def get_subclass(subclass_id: int) -> Subclass:
        return SubclassRepo.get(subclass_id)

    @staticmethod
    def list_subclasses() -> list[Subclass]:
        return SubclassRepo.list_all()

    @staticmethod
    def update_subclass(subclass_id: int, updates: dict) -> None:
        SubclassRepo.update(subclass_id, updates)

    @staticmethod
    def delete_subclass(subclass_id: int) -> None:
        SubclassRepo.delete(subclass_id)