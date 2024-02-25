import os
from django.views import View
from bson.objectid import ObjectId
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse

from .workers.connection import collection
from .workers.selection import activity_selection
from .workers.helper import export_to_excel, add_timestamp, isValid, insert_to_db, get_all_trains

# Set base and static directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'selection', 'static')

def index(request):
    if request.method == 'POST':
        # Add timestamps to the incoming request data
        data = add_timestamp(request.POST)
        # Validate the data
        is_valid, error_message = isValid(data)

        if not is_valid:
            # If data is not valid, render index page with error message
            newdata = get_all_trains()
            return render(request, 'index.html', {'newdata': newdata, 'error': error_message})

        # Insert valid data into the database
        insert_to_db(data)

        # Retrieve updated data from the database
        newdata = get_all_trains()

        # Render index page with updated data
        return render(request, 'index.html', {'newdata': newdata})
    else:
        if collection.count_documents({}) == 0:
            # Render index page if no data is present in the database
            return render(request, 'index.html')
        else:
            # Retrieve data from the database
            newdata = get_all_trains()
            # Render index page with data
            return render(request, 'index.html', {'newdata': newdata})


def delete(request, data_id):
    if request.method == 'POST':
        # Delete a record from the database
        collection.delete_one({'_id': ObjectId(data_id)})

    return redirect('index')


def sort_by_departure(request):
    if request.method == 'POST' and collection.count_documents({}) > 0:
        # Perform activity selection based on the request
        selected_activities, remaining_activities = activity_selection(request)

        # Export selected and remaining activities to Excel
        export_to_excel(selected_activities, remaining_activities)

        # Render the selection page with the selected and remaining activities
        return render(request, 'selection.html', {'platform': selected_activities, 'remaining_activity': remaining_activities})
    else:
        # Redirect to index page if no data is present in the database
        return redirect('index')


class DownloadFileView(View):
    def get(self, request, filename):
        # Serve the requested file for download
        file_path = os.path.join(STATIC_DIR, filename)
        response = FileResponse(open(file_path, 'rb'))
        return response
