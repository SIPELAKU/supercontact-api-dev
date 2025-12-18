# AUTH
from .auth_schema import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterResponse,
    UserRegisterRequest,
)

# CONTACT
from .contact_schema import (
    ContactCreate,
    ContactUpdate,
    PaginatedContacts,
    ContactResponse,
    NoteCreate,
    NoteResponse,
    TaskCreate,
    TaskResponse,
    ContactDeleteResponse,
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

# MANAGE USER
from .manage_user_schema import (
    ManageUserListResponse,
    ManageUserResponse,
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    UserLevel,
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
)

# RESPONSE
from .response_schema import ResponseModel

# USER
from .user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
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
