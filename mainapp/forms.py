from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import CustomUser, Event, ROLE_CHOICES, EventMemory
import datetime

class CustomUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(required=False, label='Profile Picture')
    enrollment_no = forms.CharField(required=False)
    department = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'enrollment_no', 'department', 'profile_image', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Department
        self.fields['department'].queryset = Department.objects.all()

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['student', 'admin']:
            raise forms.ValidationError("Only Students and Event Admins can register directly.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        enrollment_no = cleaned_data.get('enrollment_no')
        department = cleaned_data.get('department')

        if role == 'student' and not enrollment_no:
            self.add_error('enrollment_no', 'Enrollment number is required for students.')
        elif role == 'admin' and not department:
            self.add_error('department', 'Department is required for event admins.')

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")


class EventForm(forms.ModelForm):
    # Add a time field that doesn't exist in the model
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    ticket_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'image', 'available_tickets', 'ticket_price', 'department', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean_date(self):
        date = self.cleaned_data.get('date')
        from django.utils import timezone
        if date:
            if isinstance(date, datetime.datetime):
                date = date.date()
            if date < timezone.now().date():
                raise forms.ValidationError("Event date cannot be in the past.")
        return date
        
    def clean_available_tickets(self):
        tickets = self.cleaned_data.get('available_tickets')
        if tickets is not None and tickets <= 0:
            raise forms.ValidationError("Number of available tickets must be greater than zero.")
        return tickets
        
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if not date:
            raise forms.ValidationError("Date is required.")
        
        if not time:
            raise forms.ValidationError("Time is required.")
        
        if isinstance(date, datetime.datetime):
            date = date.date()
        
        # Combine date and time into a datetime object
        combined_datetime = datetime.datetime.combine(date, time)
        cleaned_data['date'] = combined_datetime
        
        # Make combined_datetime timezone-aware and validate it's not in the past
        combined_datetime = timezone.make_aware(combined_datetime)
        cleaned_data['date'] = combined_datetime
        
        if combined_datetime < timezone.now():
            raise forms.ValidationError("Event date and time must be in the future.")
        
        return cleaned_data


class SuggestEventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark the form as a suggestion
        self.is_suggestion = True
        
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class EventMemoryForm(forms.ModelForm):
    class Meta:
        model = EventMemory
        fields = ['caption']

    def save(self, commit=True):
        # This form is for multiple images, so we'll handle saving in the view
        # We'll just return the instance for now, without saving images directly
        instance = super().save(commit=False)
        return instance

# Add this at the end of the file
class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField(required=False, label='Profile Picture')
    department = forms.ModelChoiceField(queryset=None, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'enrollment_no', 'department', 'profile_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Department
        self.fields['department'].queryset = Department.objects.all()

        if self.instance:
            if self.instance.role == 'student':
                self.fields['enrollment_no'].required = True
                self.fields['department'].required = False
            elif self.instance.role == 'teacher':  # Role check for teacher
                self.fields['enrollment_no'].required = False
                self.fields['department'].required = True
            else:
                self.fields['enrollment_no'].required = False
                self.fields['department'].required = False
