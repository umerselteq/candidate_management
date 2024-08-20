from django.db import models
from django_softdelete.models import SoftDeleteModel


class BaseModel(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Candidate(BaseModel):
    parentId = models.ForeignKey('Candidate', related_name='childCandidates', null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    firstName = models.CharField(max_length=100, null=False, blank=False)
    middleName = models.CharField(max_length=100, null=True, blank=True)
    lastName = models.CharField(max_length=100, null=False, blank=False)
    designation = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=False, blank=False, unique=True)
    imageUrl = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=False, blank=False)
    dob = models.CharField(max_length=100, null=False, blank=False)
    age = models.CharField(max_length=100, null=False, blank=False)
    addressLine1 = models.CharField(max_length=100, null=True, blank=True)
    addressLine2 = models.CharField(max_length=100, null=True, blank=True)
    postalcode = models.CharField(max_length=100, null=True, blank=True)
    nationalTaxNumber = models.CharField(max_length=100, null=True, blank=True)
    primaryMobile = models.CharField(max_length=100, null=True, blank=True, unique=True)
    hasServiceProvider = models.CharField(max_length=100, null=True, blank=True)
    isActive = models.CharField(max_length=100, null=True, blank=True, default="False")
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    kinFirstName = models.CharField(max_length=100, null=True, blank=True)
    kinLastName = models.CharField(max_length=100, null=True, blank=True)
    kinMobile = models.CharField(max_length=100, null=True, blank=True)
    kinAddress = models.CharField(max_length=100, null=True, blank=True)
    kinEmail = models.EmailField(max_length=100, null=True, blank=True)
    ProjectId = models.CharField(max_length=100, null=True, blank=True)
    providerId = models.CharField(max_length=100, null=True, blank=True)
    contractorId = models.CharField(max_length=100, null=True, blank=True)
    hasSchedule = models.CharField(max_length=100, null=True, blank=True)
    centerAddressId = models.CharField(max_length=100, null=True, blank=True)
    workingAddressId = models.CharField(max_length=100, null=True, blank=True)
    staffId = models.CharField(max_length=100, null=False, blank=False)
    businessId = models.CharField(max_length=100, null=False, blank=False)
    flow = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"candidate {self.id} - {self.firstName} for business {self.businessId}"


class CandidateStatus(BaseModel):
    """status Choices will be business specific and on candidate Creation
     here we will have a default status for candidate and on completion of onboarding flow status will be Applied"""

    # Todo Status Choices will be business Specific and dynamic

    STATUS_CHOICES = [("review pending", "Review Pending"), ("registered", "Registered"), ("completed", "Completed"),
                      ("pending", "Pending"), ("suspended", "Suspended"), ("applied", "Applied"),
                      ("flow assigned", "Flow Assigned")]
    candidateId = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(choices=STATUS_CHOICES, default="registered", max_length=20)
    details = models.JSONField(null=True, blank=True)
    createdBy = models.PositiveBigIntegerField(null=True, blank=True)
