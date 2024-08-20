import factory
from candidate.models import *
from faker import Faker
fake = Faker()


class CandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Candidate

    title = factory.Faker('job')
    firstName = factory.Faker('first_name')
    middleName = factory.Faker('last_name')
    lastName = factory.Faker('last_name')
    designation = factory.Faker('word')
    qualification = factory.Faker('word')
    nationality = factory.Faker('country')
    country = factory.Faker('country')
    city = factory.Faker('city')
    mobile = factory.Faker('phone_number')
    imageUrl = factory.Faker('image_url')
    gender = factory.Faker('random_element', elements=['Male', 'Female', 'Other'])
    dob = factory.Faker('date_of_birth', minimum_age=18, maximum_age=99)
    age = factory.LazyAttribute(lambda o: str(2024 - o.dob.year))  # Assuming the current year is 2024
    addressLine1 = factory.Faker('street_address')
    addressLine2 = factory.Faker('secondary_address')
    postalcode = factory.Faker('postalcode')
    nationalTaxNumber = factory.Faker('uuid4')
    primaryMobile = factory.Faker('phone_number')
    hasServiceProvider = factory.Faker('word')
    isActive = factory.Faker('boolean')
    email = factory.Faker('email')
    kinFirstName = factory.Faker('first_name')
    kinLastName = factory.Faker('last_name')
    kinMobile = factory.Faker('phone_number')
    kinAddress = factory.Faker('street_address')
    kinEmail = factory.Faker('email')
    ProjectId = factory.Faker('uuid4')
    providerId = factory.Faker('uuid4')
    contractorId = factory.Faker('uuid4')
    hasSchedule = factory.Faker('word')
    centerAddressId = factory.Faker('uuid4')
    workingAddressId = factory.Faker('uuid4')
    staffId = factory.Faker('uuid4')
    businessId = factory.Faker('uuid4')
    flow = factory.Faker('word')


class CandidateStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CandidateStatus

    candidateId = factory.SubFactory(CandidateFactory)
    status = factory.Faker('random_element')
    details = factory.Faker('text')
    createdBy = factory.Faker('first_name')
