from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

# Create your models here.

def validate_phone_number(value):
        if not value.isdigit():
           raise ValidationError("Enter a valid phone number")
        else:
            return value

def validate_password(passwd):
    """Check if the password is valid.

    This function checks the following conditions
    if it has at least one uppercase letter
    if it has at least one lowercase letter
    if it has at least one numeral
    if it has any of the required special symbols
    """
    SpecialSym=['$','@','#','_']

    if not any(char.isdigit() for char in passwd):
        raise ValidationError('the password should have at least one numeral')
        
    elif not any(char.isupper() for char in passwd):
        raise ValidationError('the password should have at least one uppercase letter')
        
    elif not any(char.islower() for char in passwd):
        raise ValidationError('the password should have at least one lowercase letter')
        
    elif not any(char in SpecialSym for char in passwd):
        raise ValidationError('the password should have at least one of the symbols $, @, #, _')
        
    else:
       return passwd

class UserModel(models.Model):
    username = models.CharField(max_length=200,blank='False',null='False')
    email = models.EmailField(max_length=200,blank='False',null='False')
    college_name = models.CharField(max_length=200,blank='False',null='False')

    YEARS=(
        ('ONE','1st year'),
        ('TWO','2nd year'),
        ('THREE','3rd year'),
        ('FOUR','4th year'),

    )
    year = models.CharField(max_length=20,choices=YEARS,blank='False',null='False')

    GENDER=(
        ('M','Male'),
        ('F','Female'),
        ('O','Others'),
    )
    gender = models.CharField(max_length=20,choices=GENDER,blank='False',null='False')

    mobile_no=models.CharField(
        max_length=10,
        blank='False',
        null='False',
        validators=[MinLengthValidator(10),validate_phone_number])
  
    password = models.CharField(
        max_length=20,
        blank='False',
        null='False',
        validators=[MinLengthValidator(8),validate_password]
    )
    
    is_cleaned = False
    def clean(self):
        if(self.password!=self.confirm_password):
            raise ValidationError('The password and confirm password are not same!')
        else: self.is_cleaned=True

    def save(self, *args, **kwargs):
        if not self.is_cleaned:
            self.clean()
        super().save(*args, **kwargs)


    confirm_password = models.CharField(
        max_length=20,
        blank='False',
        null='False',
        validators=[MinLengthValidator(8),validate_password]
    )

    # referral code generated for user
    user_referral_code = models.CharField(max_length=6,blank='False',null='False')

    # referral code of the other user
    referral_code = models.CharField(max_length=6,blank='True',null='True')

    def __str__(self):
        return f'{self.username}'

    