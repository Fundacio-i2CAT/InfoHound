from django.urls import path
from . import views

urlpatterns = [
    # Add other URL patterns if necessary
    path('', views.index, name='index'),
    path('get_people/', views.people_view, name='people_view'),
    path('people_all/', views.people_all, name='people_all'),
    path('person_details/<int:person_id>/', views.get_person_details, name='get_person_details'),
    path('get_emails/<int:domain_id>/', views.emails_view, name='emails_view'),
    path('domain/<int:domain_id>/', views.domain_info, name='domain'),
    path('domain/add/', views.add_domain, name='add_domain'),
    path('people_count/<int:domain_id>/', views.people_count, name='people_count'),
    path('files_count/<int:domain_id>/', views.files_count, name='files_count'),
    path('subdomains_count/<int:domain_id>/', views.subdomains_count, name='subdomains_count'),
    path('emails_count/<int:domain_id>/', views.emails_count, name='emails_count'),
    path('urls_count/<int:domain_id>/', views.urls_count, name='urls_count'),
    path('emails_stats/<int:domain_id>/', views.get_emails_stats, name='emails_stats'),
    path('get_tasks/', views.get_available_tasks, name='get_available_tasks'),
    path('execute_task/', views.execute_task, name='execute_task'),
    path('get_tasks/', views.get_available_tasks, name='get_available_tasks'),
    path('get_task_status/', views.get_task_status, name='get_task_status'),
    path('get_domains/', views.get_domains, name='get_domains'),
    path('get_dorks_results/', views.get_dorks_results, name='get_dorks_results'),
    path('delete/<int:domain_id>', views.delete_domain, name='delete_domain'),

    # HTML TABS
    path('general/', views.get_general_view, name='general'),
    path('people/', views.get_people_view, name='people'),
    path('emails/', views.get_emails_view, name='emails'),
    path('tasks/', views.get_tasks_view, name='tasks'),
    path('dorks/', views.get_dorks_view, name='dorks'),
]
