
from datetime import datetime, timedelta
from .models import bookslot
from django.shortcuts import render

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import math
from datetime import date, datetime, timedelta

from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth.models import User
from pytz import timezone
import time
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


def index(request):

    # days = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # ]
    # matrix = bookslot(week=days)
    # matrix.save()
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, 'mainpage_index.html', {'username': username})
    return render(request, 'mainpage_index.html')


def book_now(request):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, 'booking_index.html', {'username': username})
    return render(request, 'booking_index.html')


def turf_details(request):
    currentDate = date.today().strftime("%Y-%m-%d")
    endDate = (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")
    return render(request, 'turfblog.html', {'currentDate': currentDate, 'endDate': endDate})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('book_now')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'signIn.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['emailid']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username Taken')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email is already Taken')
            return redirect('signup')
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email)
            user.save()
            return redirect('login')
    else:
        return render(request, 'signUp.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def contactus(request):
    return render(request, 'contactUs.html')


def aboutus(request):
    return render(request, 'aboutus.html')


def booking(request, id):
    if request.method == 'POST':
        username = request.POST['username']
        lastName = request.POST['lastName']
        fromCity = request.POST['fromCity']
        toCity = request.POST['toCity']
        depatureDate = request.POST['depatureDate']
        days = request.POST['days']
        noOfRooms = int(request.POST['noOfRooms'])
        noOfAdults = int(request.POST['noOfAdults'])
        noOfChildren = int(request.POST['noOfChildren'])
        email = request.POST['email']
        phoneNo = request.POST['phoneNo']
        totalAmount = int(request.POST['totalAmount'])

        request.session['fname'] = username
        request.session['lname'] = lastName
        request.session['to_city'] = toCity
        request.session['from_city'] = fromCity
        request.session['depature_date'] = depatureDate
        request.session['arrival_date'] = days
        request.session['no_of_rooms'] = noOfRooms
        request.session['no_of_adults'] = noOfAdults
        request.session['no_of_children'] = noOfChildren
        request.session['email'] = email
        request.session['phone_no'] = phoneNo
        request.session['total_amount'] = totalAmount

        requiredRooms = 1
        if noOfAdults/3 > 1:
            requiredRooms = math.ceil(noOfAdults/3)

        if noOfRooms < requiredRooms:
            noOfRooms = requiredRooms - noOfRooms
            messages.info(
                request, 'For adding more travellers, Please add' + str(noOfRooms) + ' more rooms')
            return redirect('booking', id)

        if noOfRooms > noOfAdults:
            messages.info(request, 'Minimum 1 Adult is required per Room')
            return redirect('booking', id)

        if (noOfAdults + noOfChildren)/4 > 1:
            requiredRooms = math.ceil((noOfAdults + noOfChildren)/4)

        if noOfRooms < requiredRooms:
            noOfRooms = requiredRooms - noOfRooms
            messages.info(
                request, 'For adding more travellers, Please add' + str(noOfRooms) + 'more rooms')
            return redirect('booking', id)

        noOfRooms = requiredRooms
        request.session['no_of_rooms'] = noOfRooms
        print("No of rooms = ", noOfRooms)
        print("Working")
        return redirect('receipt')
    else:
        return render(request, 'booking.html')


@login_required(login_url='/accounts/login')
def receipt(request):
    first_name = request.session.get('fname')
    print(first_name)
    last_name = request.session.get('lname')
    print(last_name)

    tour_amount = int(request.session.get('total_amount'))  # Per person
    print(tour_amount)
    adults = int(request.session.get('no_of_adults'))
    print(adults)
    rooms = int(request.session.get('no_of_rooms'))
    print(rooms)
    children = int(request.session.get('no_of_children'))
    print(adults)
    if rooms > 1:
        totalCost = tour_amount*adults + tour_amount*children/2 + rooms*tour_amount/4
    else:

        totalCost = tour_amount*adults + tour_amount*children/2

    request.session['total_amount'] = str(totalCost)
    print("Hello")

    print(totalCost)
    request.session['total_amount'] = tour_amount

    today = date.today()

    t = time.localtime()
    currentTime = time.strftime("%H:%M:%S", t)
    return render(request, 'receipt.html', {'totalCost': totalCost, 'date': today, 'currentTime': currentTime})


def search(request):

    # dests = Destination.objects.all()
    query = request.GET['query']
    budget = request.GET['budget']
   
    print(query)
    





update = {"1"}


@login_required(login_url='login')
def slot_details(request):
    if request.method == 'POST':
        selectedDate = request.POST['selectedDate']
        # Print the selected date for debugging
        print("Selected Date: ", selectedDate)

    # Check if there is already an instance of bookslot
    try:
        matrix = bookslot.objects.get(id='1')  # Fetch existing instance
        # Debugging fetched matrix
        print("Matrix fetched from DB: ", matrix.week)
        # Access slots for a particular day (e.g., Monday)
        monday_slots = matrix.week[0]
        print(monday_slots)  # Output: [0, 1, 0, ..., 1]
    except bookslot.DoesNotExist:
        # Initialize if not exists
        days = [[0]*20 for _ in range(7)]  # Create a 7x20 matrix
        matrix = bookslot(week=days)  # Ensure the week attribute is set
        matrix.save()
        # Debugging initialized matrix
        print("Matrix initialized: ", matrix.week)

    print("Matrix Before: ", matrix.week)  # Debugging before any updates

    choosenDay = datetime.strptime(selectedDate, "%Y-%m-%d").strftime("%A")
    currentDate = datetime.now().strftime("%Y-%m-%d")
    print("Chosen Day: ", choosenDay)  # Print the chosen day for debugging

    # Remove data for the previous day if necessary
    # if currentDate in update:
    #     dayTobeDeleted = (datetime.now() - timedelta(days=1)).strftime("%A")
    #     update.remove(currentDate)
    #     print("Day to be deleted: ", dayTobeDeleted)

    #     day_index = {
    #         "Monday": 0,
    #         "Tuesday": 1,
    #         "Wednesday": 2,
    #         "Thursday": 3,
    #         "Friday": 4,
    #         "Saturday": 5,
    #         "Sunday": 6
    #     }.get(dayTobeDeleted, None)

    #     if day_index is not None:
    #         # Reset the slots for the previous day
    #         matrix.week[day_index] = [0] * 20
    #         # Print the reset day slots
    #         print(
    #             f"Resetting slots for {dayTobeDeleted}: ", matrix.week[day_index])

    # Ensure the current day is in the array
    day_index = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }.get(choosenDay)

    # Debugging chosen day's index
    print("Day Index for Chosen Day: ", day_index)

    if day_index is not None:
        try:
            # Get the slots for the chosen day
            ls = list(map(str, matrix.week[day_index]))
            # Print the slots for the chosen day
            print("Slots for Chosen Day: ", ls)
        except IndexError as e:
            # Catch index error for debugging
            print(f"Error accessing matrix.week at index {day_index}: {e}")
            ls = []  # Fallback in case of an error
    else:
        # Debugging when day index is None
        print("Chosen day not found in the week index.")
        ls = []

    print("Matrix After: ", matrix.week)  # Debugging after updates
    return render(request, 'turfBooking.html', {
        'currentDate': currentDate,
        'selectedDate': selectedDate,
        'list': ls
    })


def turfDateSelection(request):

    if request.method == 'POST':
        selectedDate = request.POST['selectedDate']
        request.session['choosenDate'] = selectedDate
        return redirect('turf_bookings')
    else:
        currentDate = date.today().strftime("%Y-%m-%d")
        # print(currentDate)
        endDate = (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")
        return render(request, 'turfDateSelection.html', {'currentDate': currentDate, 'endDate': endDate})


def turfBilling(request):
    if request.method == 'POST':
        currentDate = date.today().strftime("%Y-%m-%d")
        selectedDate = request.POST['date']
        list_of_input_ids = request.POST.getlist('id')

        bookedSlots = []
        selectedTime = []

        for i in list_of_input_ids:
            if i == '1':
                bookedSlots.append('6-7 am')
                selectedTime.append('06:00:00')
            elif i == '2':
                bookedSlots.append('7-8 am')
                selectedTime.append('07:00:00')
            elif i == '3':
                bookedSlots.append('8-9 am')
                selectedTime.append('08:00:00')
            elif i == '4':
                bookedSlots.append('9-10 am')
                selectedTime.append('09:00:00')
            elif i == '5':
                bookedSlots.append('10-11 am')
                selectedTime.append('10:00:00')
            elif i == '6':
                bookedSlots.append('11-12 am')
                selectedTime.append('11:00:00')
            elif i == '7':
                bookedSlots.append('12-1 pm')
                selectedTime.append('12:00:00')
            elif i == '8':
                bookedSlots.append('1-2 pm')
                selectedTime.append('13:00:00')
            elif i == '9':
                bookedSlots.append('2-3 pm')
                selectedTime.append('14:00:00')
            elif i == '10':
                bookedSlots.append('3-4 pm')
                selectedTime.append('15:00:00')
            elif i == '11':
                bookedSlots.append('4-5 pm')
                selectedTime.append('16:00:00')
            elif i == '12':
                bookedSlots.append('5-6 pm')
                selectedTime.append('17:00:00')
            elif i == '13':
                bookedSlots.append('6-7 pm')
                selectedTime.append('18:00:00')
            elif i == '14':
                bookedSlots.append('7-8 pm')
                selectedTime.append('19:00:00')
            elif i == '15':
                bookedSlots.append('8-9 pm')
                selectedTime.append('20:00:00')
            elif i == '16':
                bookedSlots.append('9-10 pm')
                selectedTime.append('21:00:00')
            elif i == '17':
                bookedSlots.append('10-11 pm')
                selectedTime.append('22:00:00')
            elif i == '18':
                bookedSlots.append('11-12 pm')
                selectedTime.append('23:00:00')
            elif i == '19':
                bookedSlots.append('12-1 am')
                selectedTime.append(':00:00')

        totalAmount = len(bookedSlots) * 700
        booking_time = datetime.now(
            timezone("Asia/Kolkata")).strftime('%H:%M:%S')

        # Save booking details directly without Razorpay
        turf = TurfBooked(
            name=request.user.username,
            email=request.user.email,
            amount=totalAmount,
            selected_date=selectedDate,
            current_date=currentDate,
            booking_time=booking_time,
            slots=bookedSlots,
        )
        turf.save()

        # Prepare booking details for confirmation display
        details = {
            'username': request.user.username,
            'email': request.user.email,
            'selectedDate': selectedDate,
            'currentDate': currentDate,
            'bookedSlots': bookedSlots,
            'totalAmount': totalAmount,
            'list_of_input_ids': list_of_input_ids,
        }
        payment_id = 1
        return render(request, 'turfBilling.html', {'payment': payment_id, 'details': details})

    return render(request, 'turfBilling.html', {'details': details})


@csrf_exempt
def success(request):
    if request.method == "POST":
        total_amount = request.POST.get('total_amount')
        username = request.POST.get('username')
        email = request.POST.get('email')
        selected_date = request.POST.get('selected_date')
        current_date = request.POST.get('current_date')
        slots = request.POST.getlist('slots')
        print(slots)
        booking_time = datetime.now(
            timezone("Asia/Kolkata")).strftime('%H:%M:%S')

        bookedSlots = []
        for i in slots:
            if i == '6-7 am':
                bookedSlots.append(1)
            elif i == '7-8 am':
                bookedSlots.append(2)
            elif i == '8-9 am':
                bookedSlots.append(3)
            elif i == '9-10 am':
                bookedSlots.append(4)
            elif i == '10-11 am':
                bookedSlots.append(5)
            elif i == '11-12 am':
                bookedSlots.append(6)
            elif i == '12-1 pm':
                bookedSlots.append(7)
            elif i == '1-2 pm':
                bookedSlots.append(8)
            elif i == '2-3 pm':
                bookedSlots.append(9)
            elif i == '3-4 pm':
                bookedSlots.append(10)
            elif i == '4-5 pm':
                bookedSlots.append(11)
            elif i == '5-6 pm':
                bookedSlots.append(12)
            elif i == '6-7 pm':
                bookedSlots.append(13)
            elif i == '7-8 pm':
                bookedSlots.append(14)
            elif i == '8-9 pm':
                bookedSlots.append(15)
            elif i == '9-10 pm':
                bookedSlots.append(16)
            elif i == '10-11 pm':
                bookedSlots.append(17)
            elif i == '11-12 pm':
                bookedSlots.append(18)
            elif i == '12-1 am':
                bookedSlots.append(19)

        choosenDay = datetime.strptime(
            selected_date, "%Y-%m-%d").strftime("%A")
        print(choosenDay)
        matrix = bookslot.objects.get(id='1')
        if choosenDay == "Monday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[0][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Tuesday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[1][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Wednesday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[2][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Thursday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[3][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Friday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[4][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Saturday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[5][int(i)] = 1
                        matrix.save()
        elif choosenDay == "Sunday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (int(i) == j):
                        matrix.week[6][int(i)] = 1
                        matrix.save()
        # book.save()

        return redirect('book_now')

        

    return render(request, 'success.html')


def deleteRecord(dayTobeDeleated):
    matrix = bookslot.objects.get(id='1')
    if dayTobeDeleated == "Monday":
        for i in range(20):
            matrix.week[0][i] = 0
    elif dayTobeDeleated == "Tuesday":
        for i in range(20):
            matrix.week[1][i] = 0
    elif dayTobeDeleated == "Wednesday":
        for i in range(20):
            matrix.week[2][i] = 0
    elif dayTobeDeleated == "Thursday":
        for i in range(20):
            matrix.week[3][i] = 0
    elif dayTobeDeleated == "Friday":
        for i in range(20):
            matrix.week[4][i] = 0
    elif dayTobeDeleated == "Saturday":
        for i in range(20):
            matrix.week[5][i] = 0
    elif dayTobeDeleated == "Sunday":
        for i in range(20):
            matrix.week[6][i] = 0





@login_required(login_url='login')
def orderHistory(request):
    
    # Fetch all bookings
    bookings = TurfBooked.objects.all()
    # Fetch bookings for the logged-in user based on email
    my_bookings = TurfBooked.objects.filter(email=request.user.email)
    bookedSlots = []
    for booking in my_bookings:
        for i in booking.slots:
            if i == '1':
                bookedSlots.append('6-7 am')
            elif i == '2':
                bookedSlots.append('7-8 am')
            elif i == '3':
                bookedSlots.append('8-9 am')
            elif i == '4':
                bookedSlots.append('9-10 am')
            elif i == '5':
                bookedSlots.append('10-11 am')
            elif i == '6':
                bookedSlots.append('11-12 am')
            elif i == '7':
                bookedSlots.append('12-1 pm')
            elif i == '8':
                bookedSlots.append('1-2 pm')
            elif i == '9':
                bookedSlots.append('2-3 pm')
            elif i == '10':
                bookedSlots.append('3-4 pm')
            elif i == '11':
                bookedSlots.append('4-5 pm')
            elif i == '12':
                bookedSlots.append('5-6 pm')
            elif i == '13':
                bookedSlots.append('6-7 pm')
            elif i == '14':
                bookedSlots.append('7-8 pm')
            elif i == '15':
                bookedSlots.append('8-9 pm')
            elif i == '16':
                bookedSlots.append('9-10 pm')
            elif i == '17':
                bookedSlots.append('10-11 pm')
            elif i == '18':
                bookedSlots.append('11-12 pm')
            elif i == '19':
                bookedSlots.append('12-1 am')

    currentDate = date.today().strftime("%Y-%m-%d")
    # currentDate = '2021-08-18'
    return render(request, 'orderHistory.html', {'bookings': my_bookings, 'currentDate': currentDate})


def delete_booking(request, id):

    if request.method == 'POST':

        booking = TurfBooked.objects.get(id=id)
        selectedDate = booking.selected_date
        slots = booking.slots

        bookedSlots = []
        for i in slots:
            if i == '6-7 am':
                bookedSlots.append(1)
            elif i == '7-8 am':
                bookedSlots.append(2)
            elif i == '8-9 am':
                bookedSlots.append(3)
            elif i == '9-10 am':
                bookedSlots.append(4)
            elif i == '10-11 am':
                bookedSlots.append(5)
            elif i == '11-12 am':
                bookedSlots.append(6)
            elif i == '12-1 pm':
                bookedSlots.append(7)
            elif i == '1-2 pm':
                bookedSlots.append(8)
            elif i == '2-3 pm':
                bookedSlots.append(9)
            elif i == '3-4 pm':
                bookedSlots.append(10)
            elif i == '4-5 pm':
                bookedSlots.append(11)
            elif i == '5-6 pm':
                bookedSlots.append(12)
            elif i == '6-7 pm':
                bookedSlots.append(13)
            elif i == '7-8 pm':
                bookedSlots.append(14)
            elif i == '8-9 pm':
                bookedSlots.append(15)
            elif i == '9-10 pm':
                bookedSlots.append(16)
            elif i == '10-11 pm':
                bookedSlots.append(17)
            elif i == '11-12 pm':
                bookedSlots.append(18)
            elif i == '12-1 am':
                bookedSlots.append(19)

        choosenDay = datetime.strptime(selectedDate, "%Y-%m-%d").strftime("%A")
        print(choosenDay)
        matrix = bookslot.objects.get(id='1')
        if choosenDay == "Monday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[0][i] = 0
                        matrix.save()
        elif choosenDay == "Tuesday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[1][i] = 0
                        matrix.save()
        elif choosenDay == "Wednesday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[2][i] = 0
                        matrix.save()
        elif choosenDay == "Thursday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[3][i] = 0
                        matrix.save()
        elif choosenDay == "Friday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[4][i] = 0
                        matrix.save()
        elif choosenDay == "Saturday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[5][i] = 0
                        matrix.save()
        elif choosenDay == "Sunday":
            for i in bookedSlots:
                for j in range(1, 20):
                    if (i == j):
                        matrix.week[6][i] = 0
                        matrix.save()

        TurfBooked.objects.filter(id=id).delete()

        return redirect('index')


def allBookings(request):
    datesInSortedOrder = []
    bookings = TurfBooked.objects.filter(
        paid=True).order_by('selected_date', 'booking_time')
    currentDate = date.today().strftime("%Y-%m-%d")
    # currentDate = '2021-08-19'
    return render(request, 'allBookings.html', {'bookings': bookings, 'dates': datesInSortedOrder, 'currentDate': currentDate})


def searchBooking(request):

    query = request.POST['query']
    print(query)
    bookings = TurfBooked.objects.filter(name__icontains=query)
    print(bookings)
    return render(request, 'allBookings.html', {'bookings': bookings, 'query': query})
    # return HttpResponse('This is search')



