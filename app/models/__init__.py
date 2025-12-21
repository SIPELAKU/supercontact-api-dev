from .contact_model import Contact, ContactTask, ContactNote
from .lead_model import (
    Lead,
    LeadStatus,
    LeadSource,
    LeadTag,
    LeadIndustry,
    LeadCompanySize
)
from .mailing_model import Mailing
from .note_model import Note
from .pipeline_model import Pipeline, DealStage
from .product_model import Product
from .quotation_model import Quotation, QuotationItem, QuotationStatus
from .user_model import (
    User,
    UserRole,
    UserStatus,
    RolePermission,
    UserPosition,
    UserOTP,
    UserOTPType,
)
from .userdevice_model import UserDevice
from .userprofile_model import UserDetail
from .chat_model import ChatMessage
