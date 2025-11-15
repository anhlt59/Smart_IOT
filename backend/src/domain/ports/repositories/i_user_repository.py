"""User Repository Interface"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ...entities.user import User


class IUserRepository(ABC):
    """Interface for user data access"""

    @abstractmethod
    def save(self, user: User) -> User:
        """Save user"""
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    @abstractmethod
    def find_by_organization(self, organization_id: str) -> List[User]:
        """Find all users in organization"""
        pass

    @abstractmethod
    def update(self, user_id: str, updates: Dict) -> User:
        """Update user"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete user"""
        pass

    @abstractmethod
    def add_device_token(self, user_id: str, token: str) -> bool:
        """Add device token for push notifications"""
        pass

    @abstractmethod
    def remove_device_token(self, user_id: str, token: str) -> bool:
        """Remove device token"""
        pass
