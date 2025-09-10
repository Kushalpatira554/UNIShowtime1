from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import CustomUserRegisterForm, CustomLoginForm, ProfileEditForm, SuggestEventForm
from .models import CustomUser, Event, Ticket, Department, EventMemory

def register_view(request):
    from .models import Department
    
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            # Add specific error messages for form validation failures
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserRegisterForm()
    
    departments = Department.objects.all()
    return render(request, 'auth/register.html', {
        'form': form,
        'departments': departments
    })

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            # Add specific error messages for login failures
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            
            # Check for non-field errors (authentication failures)
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
    else:
        form = CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'student':
        return redirect('student_dashboard')
    elif user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'superadmin':
        return redirect('superadmin_dashboard')

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # Get upcoming events
    from django.utils import timezone
    from .models import Event, Ticket
    
    events = Event.objects.exclude(date__isnull=True, location__isnull=True).filter(date__gte=timezone.now())
    past_events = Event.objects.exclude(date__isnull=True, location__isnull=True).filter(date__lt=timezone.now())
    attended_events = Ticket.objects.filter(user=request.user)
    
    return render(request, 'dashboard/student_dashboard.html', {
        'upcoming_events': events,
        'past_events': past_events,
        'attended_events': attended_events
    })

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden
from .models import Ticket

def qr_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        return HttpResponseForbidden("You are not allowed to view this QR code.")
    return render(request, 'mainapp/show_qr.html', {'ticket': ticket})

def qr_download(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        return HttpResponseForbidden("You are not allowed to download this QR code.")
    return FileResponse(ticket.qr_code, as_attachment=True, filename=ticket.qr_code.name.split('/')[-1])

from django.shortcuts import render
from .models import Event, CustomUser, EventMemory
from django.utils import timezone
from .forms import EventMemoryForm

@login_required
def superadmin_dashboard(request):
    if request.user.role != 'superadmin':
        return redirect('dashboard')
    
    departments = Department.objects.all()
    users = CustomUser.objects.all()
    events = Event.objects.all()
    
    context = {
        'departments': departments,
        'users': users,
        'events': events,
        'total_departments': departments.count(),
        'total_users': users.count(),
        'total_events': events.count(),
    }
    
    return render(request, 'dashboard/superadmin_dashboard.html', context)

def admin_dashboard(request):
    if request.user.role not in ['teacher', 'superadmin']:
        return redirect('dashboard')
        
    # Apply filters
    all_events = Event.objects.exclude(date__isnull=True, location__isnull=True)  # Exclude suggested events
    users = CustomUser.objects.all()
    events = all_events # Initialize events here

    # Separate upcoming and past events
    current_time = timezone.now()
    upcoming_events_list = all_events.filter(date__gte=current_time).order_by('date')
    past_events_list = Event.objects.exclude(date__isnull=True, location__isnull=True).filter(date__lt=current_time).order_by('-date')
    
    # Filter users by role
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filter events by category
    category_filter = request.GET.get('category')
    if category_filter:
        events = events.filter(category=category_filter)
        
    # Calculate statistics
    total_events = Event.objects.exclude(date__isnull=True, location__isnull=True).count()
    total_bookings = Ticket.objects.count()
    upcoming_events = (
        Event.objects.exclude(date__isnull=True, location__isnull=True)
        .filter(date__gte=timezone.now())
        .order_by('date')
    )
    upcoming_events_count = upcoming_events.count()
    total_users = CustomUser.objects.count()

    # Get suggested events
    suggested_events = Event.objects.filter(date__isnull=True, location__isnull=True).select_related('created_by')

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'events': events, # This 'events' variable is used for the main 'Manage Events' section, which will now display upcoming events by default.
        'users': users,
        'suggested_events': suggested_events,
        'upcoming_events': list(upcoming_events_list),
        'past_events': past_events_list,
    })

@login_required
def filter_events(request):
    if request.user.role not in ['admin', 'superadmin']:
        return HttpResponseForbidden()
    
    category = request.GET.get('category')
    search = request.GET.get('search', '').strip()
    events = Event.objects.exclude(date__isnull=True, location__isnull=True)
    
    if category:
        events = events.filter(category=category)
    if search:
        events = events.filter(
            title__icontains=search
        )
    
    html = render_to_string('dashboard/partials/event_list.html', {
        'events': events
    })
    
    return JsonResponse({'html': html})

@login_required
@login_required
def approve_event(request, event_id):
    if request.user.role not in ['admin', 'superadmin']:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    event = get_object_or_404(Event, id=event_id)
    if not (event.date is None and event.location is None):
        return JsonResponse({'status': 'error', 'message': 'Event is not in suggested state'}, status=400)
    
    try:
        # Update event with default values
        event.date = timezone.now() + timezone.timedelta(days=7)  # Default to 7 days from now
        event.location = 'TBD'  # Default location
        event.save()
        return JsonResponse({'status': 'success', 'message': 'Event approved successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def reject_event(request, event_id):
    if request.user.role not in ['admin', 'superadmin']:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    event = get_object_or_404(Event, id=event_id)
    if not (event.date is None and event.location is None):
        return JsonResponse({'status': 'error', 'message': 'Event is not in suggested state'}, status=400)
    
    try:
        event.delete()
        return JsonResponse({'status': 'success', 'message': 'Event rejected successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def filter_users(request):
    if request.user.role not in ['admin', 'superadmin']:
        return HttpResponseForbidden()
    
    role = request.GET.get('role')
    search = request.GET.get('search', '').strip()
    users = CustomUser.objects.all()
    
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(
            username__icontains=search
        )
    
    html = render_to_string('dashboard/partials/user_list.html', {
        'users': users
    })
    
    return JsonResponse({'html': html})

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Prevent access to suggested events
    if event.date is None or event.location is None:
        if request.user.role not in ['admin', 'superadmin']:
            messages.error(request, 'This event is not yet approved.')
            return redirect('dashboard')
    user_has_ticket = False
    user_ticket = None
    
    if request.user.is_authenticated:
        user_ticket = Ticket.objects.filter(event=event, user=request.user).first()
        user_has_ticket = user_ticket is not None
    
    context = {
        'event': event,
        'user_has_ticket': user_has_ticket,
        'user_ticket': user_ticket
    }
    return render(request, 'mainapp/event_detail.html', context)

@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Prevent booking suggested events
    if event.date is None or event.location is None:
        messages.error(request, 'This event is not yet approved for booking.')
        return redirect('dashboard')
    
    # Check if user already has a ticket
    if Ticket.objects.filter(event=event, user=request.user).exists():
        messages.error(request, 'You already have a ticket for this event!')
        return redirect('event_details', event_id=event_id)
    
    # Check if tickets are available
    if event.tickets_left() <= 0:
        messages.error(request, 'Sorry, this event is sold out!')
        return redirect('event_details', event_id=event_id)
    
    # Handle payment if event is not free
    if not event.is_free:
        # Add your payment processing logic here
        # For now, we'll just create the ticket
        pass
    
    # Create ticket
    ticket = Ticket.objects.create(
        event=event,
        user=request.user
    )
    
    messages.success(request, 'Ticket booked successfully!')
    return redirect('qr_view', ticket_id=ticket.id)

@login_required
def admin_event_details(request, event_id):
    if request.user.role not in ['admin', 'superadmin']:
        return HttpResponseForbidden("You don't have permission to view this page.")
        
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event)
    
    return render(request, 'mainapp/admin_event_details.html', {
        'event': event,
        'tickets': tickets
    })

@login_required
def event_memories(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.date.date() >= timezone.now().date():
        messages.error(request, "Event memories are only available after the event has ended.")
        return redirect('event_details', event_id=event_id)
        
    user_has_ticket = False
    if request.user.is_authenticated:
        user_has_ticket = request.user.ticket_set.filter(event=event).exists()

    return render(request, 'mainapp/event_memories.html', {
        'event': event,
        'user_has_ticket': user_has_ticket
    })

@login_required
def department_details(request, department_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    from django.utils import timezone
    department = get_object_or_404(Department, id=department_id)
    users = CustomUser.objects.filter(department=department)
    
    return render(request, 'mainapp/department_details.html', {
        'department': department,
        'users': users,
        'now': timezone.now()
    })

@login_required
def create_department(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if name and code:
            Department.objects.create(name=name, code=code)
            messages.success(request, 'Department created successfully.')
            return redirect('superadmin_dashboard')
        messages.error(request, 'Please fill all required fields.')
    
    return render(request, 'mainapp/create_department.html')

@login_required
def user_details(request, user_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'mainapp/user_details.html', {'user': user})

@login_required
def edit_user(request, user_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        if request.POST.get('department'):
            user.department = get_object_or_404(Department, id=request.POST.get('department'))
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_details', user_id=user.id)
    
    departments = Department.objects.all()
    return render(request, 'mainapp/edit_user.html', {
        'user': user,
        'departments': departments
    })

@login_required
def create_user(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_details', user_id=user.id)
    else:
        form = CustomUserRegisterForm()
    
    return render(request, 'mainapp/create_user.html', {'form': form})

@login_required
def system_settings(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    if request.method == 'POST':
        setting_type = request.POST.get('setting_type')
        if setting_type == 'site':
            # Handle site settings
            site_name = request.POST.get('site_name', 'UniShowTime')
            site_description = request.POST.get('site_description', '')
            messages.success(request, 'Site settings updated successfully!')
        elif setting_type == 'email':
            # Handle email settings
            messages.success(request, 'Email settings updated successfully!')
        elif setting_type == 'security':
            # Handle security settings
            messages.success(request, 'Security settings updated successfully!')
        elif setting_type == 'api':
            # Handle API settings
            messages.success(request, 'API settings updated successfully!')
    
    return render(request, 'mainapp/system_settings.html')

@login_required
def system_logs(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # Mock log data - in real implementation, this would come from a log file or database
    logs = [
        {
            'level': 'INFO',
            'message': 'User login successful',
            'timestamp': '2024-01-15 10:30:00',
            'user': 'admin@unishowtime.com',
            'ip': '192.168.1.100'
        },
        {
            'level': 'ERROR',
            'message': 'Database connection failed',
            'timestamp': '2024-01-15 09:45:00',
            'user': 'system',
            'ip': 'localhost'
        },
        {
            'level': 'WARNING',
            'message': 'Invalid login attempt',
            'timestamp': '2024-01-15 08:20:00',
            'user': 'unknown',
            'ip': '203.0.113.50'
        }
    ]
    
    # Filter by level if provided
    level_filter = request.GET.get('level', 'all')
    if level_filter != 'all':
        logs = [log for log in logs if log['level'] == level_filter.upper()]
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        logs = [log for log in logs if search.lower() in log['message'].lower()]
    
    context = {
        'logs': logs,
        'level_filter': level_filter,
        'search': search
    }
    
    return render(request, 'mainapp/system_logs.html', context)

@login_required
def system_backup(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # Mock backup data - in real implementation, this would come from file system or cloud storage
    backups = [
        {
            'id': 1,
            'name': 'full_backup_2024_01_15',
            'type': 'full',
            'size': 52428800,  # 50MB
            'created': '2024-01-15 10:00:00',
            'path': '/backups/full_backup_2024_01_15.json'
        },
        {
            'id': 2,
            'name': 'events_backup_2024_01_14',
            'type': 'events',
            'size': 10485760,  # 10MB
            'created': '2024-01-14 15:30:00',
            'path': '/backups/events_backup_2024_01_14.json'
        }
    ]
    
    context = {
        'backups': backups,
        'backup_count': len(backups),
        'total_size': sum(backup['size'] for backup in backups),
        'last_backup': max(backups, key=lambda x: x['created'])['created'] if backups else None,
        'current_date': '2024-01-15'
    }
    
    return render(request, 'mainapp/system_backup.html', context)
from django.contrib import messages
from .forms import EventForm
import json
import os
from datetime import datetime

def create_event(request):
    # Check if user is authenticated and has appropriate permissions
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an event.")
        return redirect('login')
    
    if not (request.user.is_event_admin or request.user.is_super_admin):
        messages.error(request, "You don't have permission to create events.")
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Set the created_by field to the current user
            event.save()
            messages.success(request, "Event created successfully!")
            
            # Redirect based on user role
            if request.user.is_super_admin:
                return redirect('superadmin_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            # Print form errors for debugging
            print(form.errors)  # Optional: You can remove this after debugging
            messages.error(request, "There was an error in the form. Please check all fields.")
    else:
        form = EventForm()
        
        # Pre-select department if admin belongs to a department
        if request.user.department and hasattr(request.user, 'is_event_admin') and request.user.is_event_admin:
            form.initial['department'] = request.user.department

    # Get all departments for the dropdown
    from .models import Department
    departments = Department.objects.all()
    
    return render(request, 'mainapp/create_event.html', {
        'form': form,
        'departments': departments,
        'categories': Event.CATEGORY_CHOICES
    })

@login_required
def suggest_event(request):
    if request.method == 'POST':
        form = SuggestEventForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.created_by = request.user
            suggestion.date = None  # Set date to null for suggested events
            suggestion.location = None  # Set location to null for suggested events
            suggestion.available_tickets = 0  # Will be set by admin when approved
            suggestion.save()
            messages.success(request, "Event suggestion submitted successfully! An admin will review it.")
            return redirect('student_dashboard')
        else:
            messages.error(request, "There was an error in your suggestion. Please check all fields.")
    else:
        form = SuggestEventForm()
    return render(request, 'mainapp/suggest_event.html', {
        'form': form,
        'categories': Event.CATEGORY_CHOICES
    })

def admin_user_details(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'dashboard/admin_user_details.html', {'user': user})


@login_required
def edit_event(request, event_id):
    # Check if user is authenticated and has appropriate permissions
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit an event.")
        return redirect('login')
    
    if not (request.user.is_event_admin or request.user.is_super_admin):
        messages.error(request, "You don't have permission to edit events.")
        return redirect('student_dashboard')
    
    # Get the event or return 404
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is allowed to edit this event
    if not request.user.is_super_admin and event.department != request.user.department:
        messages.error(request, "You can only edit events from your department.")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # For POST requests, process the form data
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'student':
                user.enrollment_no = form.cleaned_data.get('enrollment_no')
            elif user.role == 'teacher':
                user.department = form.cleaned_data.get('department')
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            user.save()
            messages.success(request, "Event updated successfully!")
            
            # Redirect based on user role
            if request.user.is_super_admin:
                return redirect('superadmin_dashboard')
            else:
                return redirect('admin_dashboard')
    else:
        # For GET requests, pre-populate the form with event data
        # Extract time from the datetime field for the form
        initial_data = {'time': event.date.time()} if event.date else None
        form = EventForm(instance=event, initial=initial_data)
    
    # Get departments for the form
    departments = Department.objects.all()
    
    return render(request, 'mainapp/create_event.html', {
        'form': form,
        'departments': departments,
        'edit_mode': True,
        'event': event
    })

@login_required
def delete_event(request, event_id):
    # Check if user is authenticated and has appropriate permissions
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to delete an event.")
        return redirect('login')
    
    if not (request.user.is_event_admin or request.user.is_super_admin):
        messages.error(request, "You don't have permission to delete events.")
        return redirect('student_dashboard')
    
    # Get the event or return 404
    event = get_object_or_404(Event, id=event_id)
    
    # Check if the user is allowed to delete this event
    if not request.user.is_super_admin and event.department != request.user.department:
        messages.error(request, "You can only delete events from your department.")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # Delete the event
        event_title = event.title
        event.delete()
        messages.success(request, f"Event '{event_title}' has been deleted.")
        
        # Redirect based on user role
        if request.user.is_super_admin:
            return redirect('superadmin_dashboard')
        else:
            return redirect('admin_dashboard')
    
    # If not POST request, redirect to event details
    return redirect('admin_event_details', event_id=event_id)

@login_required
def add_event_memory(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user has permission to add memories (e.g., admin or superadmin)
    if not request.user.is_authenticated or request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "You don't have permission to add memories to this event.")
        return redirect('event_details', event_id=event.id)

    if request.method == 'POST':
        caption = request.POST.get('caption')
        images = request.FILES.getlist('images')

        if caption and images:
            for image in images:
                EventMemory.objects.create(event=event, caption=caption, image=image, shared_by=request.user)
            messages.success(request, 'Memories added successfully!')
            return redirect('event_memories', event_id=event.id)
        else:
            messages.error(request, 'Error adding memories. Please provide a caption and select at least one image.')
    
    form = EventMemoryForm()

    return render(request, 'mainapp/add_event_memory.html', {'form': form, 'event': event})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'student':
                user.enrollment_no = form.cleaned_data.get('enrollment_no')
            elif user.role == 'teacher':
                user.department = form.cleaned_data.get('department')
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')

    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'mainapp/edit_profile.html', {'form': form})

@login_required
def create_backup(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    if request.method == 'POST':
        backup_type = request.POST.get('backup_type', 'full')
        backup_name = request.POST.get('backup_name', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        include_media = request.POST.get('include_media') == 'on'
        
        # Mock backup creation - in real implementation, this would create actual backup files
        messages.success(request, f'Backup "{backup_name}" created successfully!')
        
    return redirect('system_backup')

@login_required
def restore_backup(request, backup_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    if request.method == 'POST':
        # Mock restore functionality - in real implementation, this would restore from backup
        messages.success(request, f'Backup {backup_id} restored successfully!')
    
    return redirect('system_backup')

@login_required
def download_backup(request, backup_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    # Mock download - in real implementation, this would serve the actual backup file
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="backup_{backup_id}.json"'
    
    # Create mock backup content
    backup_data = {
        'backup_id': backup_id,
        'created': datetime.now().isoformat(),
        'type': 'full',
        'data': {'users': [], 'events': [], 'bookings': []}
    }
    
    json.dump(backup_data, response, indent=2)
    return response

@login_required
def delete_backup(request, backup_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    if request.method == 'POST':
        # Mock delete functionality
        messages.success(request, f'Backup {backup_id} deleted successfully!')
    
    return redirect('system_backup')

@login_required
def clear_logs(request):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to perform this action.")
    if request.method == 'POST':
        # Mock clear logs functionality
        messages.success(request, 'All logs cleared successfully!')
    return redirect('system_logs')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_logs(request):
    # Mock implementation for exporting logs
    messages.success(request, "Logs exported successfully (mock).")
    return redirect('system_logs')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def upload_and_restore_backup(request):
    if request.method == 'POST':
        # Mock implementation for handling uploaded backup file and restoring
        messages.success(request, "Backup file uploaded and restored successfully (mock).")
    return redirect('system_backup')

def contact_view(request):
    return render(request, 'mainapp/contact.html')

@login_required
def edit_department(request, department_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if name and code:
            department.name = name
            department.code = code
            department.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('department_details', department_id=department.id)
        messages.error(request, 'Please fill all required fields.')
    
    return render(request, 'mainapp/edit_department.html', {'department': department})

@login_required
def delete_department(request, department_id):
    if request.user.role != 'superadmin':
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        department_name = department.name
        department.delete()
        messages.success(request, f'Department "{department_name}" deleted successfully.')
        return redirect('superadmin_dashboard')
    
    return redirect('department_details', department_id=department_id)
