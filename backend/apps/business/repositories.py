from .models import Business, Branch, Address, OperatingHours

class BusinessRepository:
    @staticmethod
    def create(data: dict) -> Business:
        return Business.objects.create(**data)

    @staticmethod
    def get_by_id(business_id: str) -> Business:
        return Business.available_objects.filter(id=business_id).first()

    @staticmethod
    def get_active_by_id(business_id: str) -> Business:
        return Business.active_objects.filter(id=business_id).first()

    @staticmethod
    def get_all_active():
        return Business.active_objects.all()

    @staticmethod
    def update(business: Business, data: dict) -> Business:
        for key, value in data.items():
            setattr(business, key, value)
        business.save()
        return business

    @staticmethod
    def soft_delete(business: Business) -> None:
        business.soft_delete()

class BranchRepository:
    @staticmethod
    def create(data: dict) -> Branch:
        return Branch.objects.create(**data)

    @staticmethod
    def get_by_id(branch_id: str) -> Branch:
        return Branch.objects.filter(id=branch_id).first()

    @staticmethod
    def get_by_business(business_id: str):
        return Branch.objects.filter(business_id=business_id)

    @staticmethod
    def update(branch: Branch, data: dict) -> Branch:
        for key, value in data.items():
            setattr(branch, key, value)
        branch.save()
        return branch

    @staticmethod
    def delete(branch: Branch) -> None:
        branch.delete()

class AddressRepository:
    @staticmethod
    def create(data: dict) -> Address:
        return Address.objects.create(**data)

    @staticmethod
    def get_by_id(address_id: str) -> Address:
        return Address.objects.filter(id=address_id).first()
        
    @staticmethod
    def get_by_business(business_id: str):
        return Address.objects.filter(business_id=business_id)

    @staticmethod
    def update(address: Address, data: dict) -> Address:
        for key, value in data.items():
            setattr(address, key, value)
        address.save()
        return address

    @staticmethod
    def delete(address: Address) -> None:
        address.delete()

class OperatingHoursRepository:
    @staticmethod
    def create(data: dict) -> OperatingHours:
        return OperatingHours.objects.create(**data)

    @staticmethod
    def get_by_business(business_id: str):
        return OperatingHours.objects.filter(business_id=business_id)

    @staticmethod
    def update_or_create(business_id: str, weekday: int, defaults: dict) -> OperatingHours:
        obj, created = OperatingHours.objects.update_or_create(
            business_id=business_id, weekday=weekday, defaults=defaults
        )
        return obj
