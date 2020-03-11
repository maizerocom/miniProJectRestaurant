from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.dateparse import parse_date
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.templatetags.static import static
import time
# Create your views here.

from classes.models import Restaurant, Faculty, Restaurant_food, Food
def my_login(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user: 
            login(request, user)

            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password!'

    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url
    return render(request, template_name='login.html', context=context)


def my_logout(request):
    logout(request)
    return redirect('login')

@login_required
def res_add(request):
    msg = ''
    faculty_obj = Faculty.objects.all()

    if request.method == 'POST':
        try:
            faculty_id = request.POST.get('faculty')
            res = Restaurant.objects.create(
                name = request.POST.get('name'),
                owner = request.POST.get('owner'),
                picture = request.FILES['picture'],
                open_time = request.POST.get('open_time'),
                close_time = request.POST.get('close_time'),
                rating = int(request.POST.get('rating')),
                approve_by = request.POST.get('approve_by'),
                faculty = Faculty.objects.get(pk=faculty_id)
            )
            
            msg = 'Successfully create new Restaurant - Restaurantname: %s' % (res.name)
        except:
            faculty_id = request.POST.get('faculty')
            res = Restaurant.objects.create(
                name = request.POST.get('name'),
                owner = request.POST.get('owner'),
                picture = static('/media/gallery/nopicture.jpg'),
                open_time = request.POST.get('open_time'),
                close_time = request.POST.get('close_time'),
                rating = int(request.POST.get('rating')),
                approve_by = request.POST.get('approve_by'),
                faculty = Faculty.objects.get(pk=faculty_id)
            )
            
            msg = 'Successfully create new Restaurant - Restaurantname: %s' % (res.name)

        print(request.POST.get('name'), "created")
        return redirect(to='res_list')
        
    else:
        res = Restaurant.objects.none()

    context = {
        'res': res,
        'msg': msg,
        'faculty': faculty_obj,
        'list': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    }

    return render(request, 'res_form.html', context=context)

@login_required
def res_list(request):

    search = request.GET.get('search', '')
    faculty = Faculty.objects.all()
    classes = Restaurant.objects.filter(
        name__icontains=search
    )
    return render(request, 'res_list.html', context={
        'search': search,
        'classes': classes,
        'faculty': faculty
    })

@login_required
def res_delete(request, res_id):

    res = Restaurant.objects.get(pk=res_id)
    res.delete()
    return redirect(to='res_list')

@login_required
def res_update(request, res_id):
    print(request.POST.get('rating'))
    try:
        res = Restaurant.objects.get(pk=res_id)
        faculty_obj = Faculty.objects.all()
        msg = ''
    except Restaurant.DoesNotExist:
        return redirect('res_list')
    faculty_id = request.POST.get('faculty')
    if request.method == 'POST':
        try:
            res.name = request.POST.get('name')
            res.owner = request.POST.get('owner')
            res.picture = request.FILES['picture']
            res.open_time = request.POST.get('open_time')
            res.close_time = request.POST.get('close_time')
            res.rating = request.POST.get('rating')
            res.approve_by = request.POST.get('approve_by')
            res.faculty = Faculty.objects.get(pk=faculty_id)
            res.save()
            msg = 'Successfully update Restaurant - id: %s' % (res.id)
        except:
            res.name = request.POST.get('name')
            res.owner = request.POST.get('owner')
            res.open_time = request.POST.get('open_time')
            res.close_time = request.POST.get('close_time')
            res.rating = request.POST.get('rating')
            res.approve_by = request.POST.get('approve_by')
            res.faculty = Faculty.objects.get(pk=faculty_id)
            res.save()
            msg = 'Successfully update Restaurant - id: %s' % (res.id)
        return redirect('res_list')
    context = {
        'res': res,
        'msg': msg,
        'faculty': faculty_obj
    }

    return render(request, 'res_form.html', context=context)

def resf_list(request, res_id):

    res = Restaurant.objects.get(pk=res_id)
    list_f = Restaurant_food.objects.filter(
        restaurant = res_id
    )
    return render(request, 'resf_list.html', context={
        'res_f': res,
        'list_f': list_f
    })

@login_required
def resf_delete(request, resf_id):
    res_f = Restaurant_food.objects.get(pk=resf_id)
    res_f.delete()
    return redirect(to='resf_list', res_id=res_f.restaurant.id)

@login_required
def resf_add(request, res_id):
    msg = ''
    if request.method == 'POST':
        foo = Food.objects.create(
            name = request.POST.get('name'),
            is_vegan = True
        )
        res_f = Restaurant_food.objects.create(
            food = foo,
            price = request.POST.get('price'),
            restaurant = Restaurant.objects.get(pk=res_id)
        )
        msg = 'Successfully create new Restaurant - Restaurantname: %s' % (foo.name)
        return redirect(to='resf_list', res_id=res_id)
    else:
        res_f = Restaurant_food.objects.none()

    context = {
        'res_f': res_f,
        'msg': msg,
        'res_f_id': res_id
    }
    return render(request, 'resf_form.html', context=context)

@login_required
def resf_update(request, resf_id):
    res_f = Restaurant_food.objects.get(pk=resf_id)
    fou = Food.objects.get(pk=res_f.food.id)
    if request.method == 'POST':
        fou.name = request.POST.get('name')
        fou.save()
        res_f.food = Food.objects.get(pk=res_f.food.id)
        res_f.price = request.POST.get('price')
        res_f.restaurant = Restaurant.objects.get(pk=res_f.restaurant.id)
        res_f.save()
        return redirect(to='resf_list', res_id=res_f.restaurant.id)
    context = {
        'res_f': res_f,
    }

    return render(request, 'resf_form.html', context=context)

def rating(request, resf_id):
    resf = Restaurant.objects.get(pk=resf_id)
    # fou = Food.objects.get(pk=res_f.food.id)
    if request.method == 'POST':
        resf.rating = request.POST.get('rating')
        resf.save()
        return redirect(to='resf_list', res_id=resf_id)
    # context = {
    #     'res_f': res_f,
    # }
    context = {
        'resf': resf,
    }
    return render(request, 'rating.html', context=context)

