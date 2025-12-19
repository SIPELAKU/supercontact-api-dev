# AUTH
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
# BRANCH
from .branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchRead,
    BranchReadWithDepartment,
)
# CONTACT
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
# ERROR
from .error_schema import ErrorCode, ErrorResponse
# LEAD
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
# MANAGE USER
from .manage_user_schema import (
    ManageUserListResponse,
    ManageUserResponse,
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    UserLevel,
)
from .note_schema import (
    NoteCreate,
    NoteUpdate,
    PaginatedNote,
    NoteResponse,
    NoteGetQuery
)
# PIPELINE
from .pipeline_schema import (
    PipelineRequest,
    PipelineGetQuery,
    PipelineResponse,
    PipelineUpdateStage,
    PipelineListResponse,
    PipelineAssignedUsers,
)
# PRODUCT
from .product_schema import (
    ProductGetQuery,
    ProductResponse,
    ProductRequest,
    ProductListResponse,
    ProductDeleteResponse,
)
# QUOTATION
from .quotation_schema import (
    QuotationItemRequest,
    QuotationRequest,
    QuotationItemResponse,
    QuotationResponse,
    QuotationListResponse,
    QuotationGetQuery,
    QuotationSendEmailResponse,
)
# RESPONSE
from .response_schema import ResponseModel
# USER
from .user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserGetQuery,
    PaginatedUserResponse,
    UserGetQuery,
)
# DEPARTMENT
from .department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentRead,
    DepartmentReadWithRelations,
    BranchReadSimple,
)

# BRANCH
from .branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchRead,
    BranchReadWithDepartment,
)

