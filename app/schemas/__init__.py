from .auth_schema import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterResponse,
    UserRegisterRequest,
    ResendOtpRequest,
    ResendOtpResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from .contact_schema import (
    ContactCreate,
    ContactUpdate,
    PaginatedContacts,
    ContactResponse,
    ContactNoteCreate,
    ContactNoteResponse,
    ContactTaskCreate,
    ContactTaskResponse,
    ContactDeleteResponse,
    ContactGetQuery,
    ContactSortOrder,
    ContactSortBy
)
from .error_schema import ErrorCode, ErrorResponse
from .lead_schema import (
    LeadResponse,
    LeadListResponse,
    SortOrder,
    LeadRequest,
    LeadGetQuery,
    LeadUpdateStatus,
    LeadDeleteResponse,
)
from .mailing_schema import (
    MailingCreate,
    MailingDeleteResponse,
    MailingResponse,
    MailingUpdate,
    PaginatedMailings
)
from .note_schema import (
    NoteCreate,
    NoteUpdate,
    PaginatedNote,
    NoteResponse,
    NoteGetQuery
)
from .pipeline_schema import (
    PipelineRequest,
    PipelineGetQuery,
    PipelineResponse,
    PipelineUpdateStage,
    PipelineListResponse,
    PipelineAssignedUsers,
)
from .product_schema import (
    ProductGetQuery,
    ProductResponse,
    ProductRequest,
    ProductListResponse,
    ProductDeleteResponse,
)
from .quotation_schema import (
    QuotationItemRequest,
    QuotationRequest,
    QuotationItemResponse,
    QuotationResponse,
    QuotationListResponse,
    QuotationGetQuery,
    QuotationSendEmailResponse,
)
from .response_schema import ResponseModel
from .user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserGetQuery
)
