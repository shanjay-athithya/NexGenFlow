from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse ,reverse_lazy
from django.http import JsonResponse
from django.core import serializers
from django.views import View

import json
import math
import time

from .forms import *
from .models import *
from .algorithms import *


def register_view(request):
    # Check if the request method is POST
    if request.method == 'POST':
        # Instantiate the UserCreationForm with POST data
        form = UserCreationForm(request.POST)
        
        # Check if the form is valid
        if form.is_valid():
            # Save the user form and get the new user object
            new_user = form.save()
            
            # Automatically log in the user
            login(request, new_user)
            
            # Display a success message (optional)
            messages.success(request, 'Registration successful! You are now logged in.')
            
            # Redirect the user to the desired URL after registration
            return redirect('home')  # Redirect to your desired page
            
        else:
            # Display error messages if the form is invalid (optional)
            messages.error(request, 'Registration failed. Please check the form for errors.')
    
    else:
        # If the request method is GET, instantiate a blank UserCreationForm
        form = UserCreationForm()
    
    # Render the registration form template with the form context
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Change 'home' to your actual home page URL
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def about_view(request):
    return render(request, 'about.html')

@login_required
def network_visualization(request):
    # Fetch data from the models
    nodes = Node.objects.all()
    edges = Edge.objects.all()

    # Prepare data for D3.js visualization
    node_data = [{'id': node.id, 'name': node.name, 'type': node.type, 'lat': node.latitude, 'lon': node.longitude} for node in nodes]
    edge_data = [{'source': edge.source.id, 'target': edge.target.id, 'length': edge.length, 'flow_rate': edge.flow_rate} for edge in edges]

    # Convert data to JSON format for use in the JavaScript frontend
    network_data = {
        'nodes': node_data,
        'edges': edge_data
    }
    network_data_json = json.dumps(network_data)

    # Render the template and pass the data as context
    return render(request, 'network_visualization.html', {
        'network_data_json': network_data_json
    })

@login_required
def network_management(request):
    # View for the network management page
    nodes = Node.objects.all()
    edges = Edge.objects.all()
    
    # Handle search/filtering if needed
    # Add logic to search/filter nodes and edges
    
    context = {
        'nodes': nodes,
        'edges': edges
    }
    return render(request, 'network_management.html', context)

@login_required
def create_node(request):
    # View to handle node creation
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Node created successfully.')
            return redirect(reverse('network_management'))
    else:
        form = NodeForm()
    return render(request, 'create_node.html', {'form': form})

# Function to calculate distance between two points using the Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def euclidean_distance(lat1, lon1, lat2, lon2):
    # Calculate the distance using the Euclidean distance formula
    distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5
    return distance

@login_required
def create_edge(request):
    # Fetch all available nodes to display in the dropdown
    nodes = Node.objects.all()
    
    if request.method == 'POST':
        form = EdgeForm(request.POST)
        if form.is_valid():
            edge = form.save(commit=False)
            
            # Check if an edge already exists between the selected source and target nodes
            source_node_id = form.cleaned_data['source'].id
            target_node_id = form.cleaned_data['target'].id
            
            existing_edge = Edge.objects.filter(source_id=source_node_id, target_id=target_node_id).exists()
            if existing_edge:
                messages.error(request, 'Edge already exists between these nodes.')
                return redirect('create_edge')  # Redirect back to the edge creation page
            
            # Calculate length based on latitudes and longitudes of source and target nodes
            source = get_object_or_404(Node, pk=source_node_id)
            target = get_object_or_404(Node, pk=target_node_id)
            
            # Calculate the Euclidean distance
            length = euclidean_distance(source.latitude, source.longitude, target.latitude, target.longitude)
            edge.length = length  # Update the length field
            
            edge.save()  # Save the edge with the updated length
            messages.success(request, 'Edge created successfully.')
            
            return redirect('network_visualization')  # Redirect to the visualization page
    else:
        form = EdgeForm()

    return render(request, 'create_edge.html', {
        'form': form,
        'nodes': nodes,  # Pass the list of nodes to the template
    })

@login_required
def edit_node(request, node_id):
    # View to handle node editing
    node = get_object_or_404(Node, id=node_id)
    if request.method == 'POST':
        form = NodeForm(request.POST, instance=node)
        if form.is_valid():
            form.save()
            messages.success(request, 'Node updated successfully.')
            return redirect(reverse('network_management'))
    else:
        form = NodeForm(instance=node)
    return render(request, 'edit_node.html', {'form': form})

@login_required
def edit_edge(request, edge_id):
    # View to handle edge editing
    edge = get_object_or_404(Edge, id=edge_id)
    if request.method == 'POST':
        form = EdgeForm(request.POST, instance=edge)
        
        if form.is_valid():
            edge = form.save(commit=False)
            # Calculate length based on latitudes and longitudes of source and target nodes
            source = edge.source
            target = edge.target
            length = euclidean_distance(source.latitude, source.longitude, target.latitude, target.longitude)
            edge.length = length  # Update the length field
            edge.save()  # Save the edge with the updated length
            form.save()
            messages.success(request, 'Edge updated successfully.')
            return redirect(reverse('network_management'))
    else:
        form = EdgeForm(instance=edge)
    return render(request, 'edit_edge.html', {'form': form})

@login_required
def delete_node(request, node_id):
    # View to handle node deletion
    node = get_object_or_404(Node, id=node_id)
    node.delete()
    messages.success(request, 'Node deleted successfully.')
    return redirect(reverse('network_management'))

@login_required
def delete_edge(request, edge_id):
    # View to handle edge deletion
    edge = get_object_or_404(Edge, id=edge_id)
    edge.delete()
    messages.success(request, 'Edge deleted successfully.')
    return redirect(reverse('network_management'))

class CreateNodeView(View):
    def get(self, request):
        form = NodeForm()
        return render(request, 'node_form.html', {'form': form})
    
    def post(self, request):
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home page or network visualization page
        
        return render(request, 'node_form.html', {'form': form})

class CreateEdgeView(View):
    def get(self, request):
        form = EdgeForm()
        return render(request, 'edge_form.html', {'form': form})
    
    def post(self, request):
        form = EdgeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home page or network visualization page
        
        return render(request, 'edge_form.html', {'form': form})

def get_network_data(request):
    # Fetch nodes and edges from the database
    nodes = Node.objects.all()
    edges = Edge.objects.all()

    # Serialize nodes and edges
    nodes_json = serializers.serialize('json', nodes)
    edges_json = serializers.serialize('json', edges)

    # Convert data to JSON
    network_data = {
        'nodes': nodes_json,
        'edges': edges_json
    }

    return JsonResponse(network_data)

def construct_graph_from_db():
    from .models import Edge
    
    # Initialize an empty dictionary to represent the graph
    graph = {}
    
    # Query all edges from the database
    edges = Edge.objects.all()
    
    # Iterate over each edge and construct the graph
    for edge in edges:
        source = edge.source
        target = edge.target
        weight = edge.flow_rate  # Use flow_rate as the edge weight
        
        # Add source and target to graph if not present
        if source not in graph:
            graph[source] = {}
        if target not in graph:
            graph[target] = {}
        
        # Add the edge to the graph
        graph[source][target] = weight
        
        # If the graph is undirected, add the reverse edge
        # If you want the graph to be directed, remove this part
        # Also, update the weight or use 0 if the reverse edge doesn't exist
        if target in graph and source not in graph[target]:
            graph[target][source] = 0
        
    # Return the constructed graph
    return graph

def construct_graph_from_db_diks():
    """Constructs a graph from the database and returns it as an adjacency list."""
    from .models import Edge
    
    # Initialize an empty dictionary to represent the graph
    graph = {}
    
    # Query all edges from the database
    edges = Edge.objects.all()
    
    # Iterate over each edge and construct the graph
    for edge in edges:
        source = edge.source
        target = edge.target
        weight = edge.length  # Use flow_rate as the edge weight
        
        # Add source and target to graph if not present
        if source not in graph:
            graph[source] = {}
        if target not in graph:
            graph[target] = {}
        
        # Add the edge to the graph
        graph[source][target] = weight
        
        # If the graph is undirected, add the reverse edge
        # If you want the graph to be directed, remove this part
        # Also, update the weight or use 0 if the reverse edge doesn't exist
        if target in graph and source not in graph[target]:
            graph[target][source] = 0
        
    # Return the constructed graph
    return graph

@login_required
def optimization_page(request):
    # Initialize form and results
    form = OptimizationForm(request.POST or None)
    optimization_results = None
    error_message = None
    best_algorithm = None
    pa = None
    
    if request.method == 'POST':
        if 'compare_algorithms' in request.POST:
            if form.is_valid():
                try:
                    results = {}
                    optimization_results = None
                    graph = construct_graph_from_db()
                    source = form.cleaned_data['source_node']
                    target = form.cleaned_data.get('target_node')

                    def run_algorithm(algo_name, algo_func):
                        start_time = time.time()
                        flow = algo_func(graph, source, target)
                        end_time = time.time()
                        duration = end_time - start_time
                        results[algo_name] = {
                            'flow': flow,
                            'duration': duration
                        }
                        
                    run_algorithm('Edmund-Karp', edmonds_karp)
                    run_algorithm('Ford-Fulkerson', ford_fulkerson)
                    run_algorithm('Dinic', dinic)
                    run_algorithm('Push-Relabel', push_relabel)

                    # Determine the best algorithm based on execution time
                    if results:
                        best_algorithm = min(results.items(), key=lambda x: x[1]['duration'])
                        
                    """algorithm = best_algorithm[0]
                    if algorithm == 'Edmund-Karp':
                        flow = edmonds_karp(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Edmonds-Karp algorithm with flow: {flow}")
                        
                    elif algorithm == 'Ford-Fulkerson':
                        flow = ford_fulkerson(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Ford-Fulkerson algorithm with flow: {flow}")
                        
                    elif algorithm == 'Dinic':
                        flow = dinic(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Dinic's algorithm with flow: {flow}")
                        
                    elif algorithm == 'Push-Relabel':
                        flow = push_relabel(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Push-Relabel algorithm with flow: {flow}")  
                    """
                
                except Exception as e:
                    error_message = f"An error occurred while running the optimization: {str(e)}"
                    logging.error(f"An error occurred: {e}")

        else:
            optimization_results = None
            if form.is_valid():
                try:
                    # Get cleaned data from the form
                    algorithm = form.cleaned_data['algorithm']
                    source = form.cleaned_data['source_node']
                    target = form.cleaned_data.get('target_node')

                    # Initialize optimization results
                    optimization_results = None
                    path = None
                    graph = construct_graph_from_db()
                    g = construct_graph_from_db_diks()

                    # Run the selected algorithm and compute optimization results
                    if algorithm == 'dijkstra':
                        optimization_results = dijkstra(g, source, target)
                        
                    elif algorithm == 'edmonds_karp':
                        flow, path = edmonds_karp(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Edmonds-Karp algorithm with flow: {flow}")
                        
                    elif algorithm == 'ford_fulkerson':
                        flow, path = ford_fulkerson(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Ford-Fulkerson algorithm with flow: {flow}")
                        
                    elif algorithm == 'dinic':
                        flow, path = dinic(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Dinic's algorithm with flow: {flow}")
                        
                    elif algorithm == 'push_relabel':
                        flow, path = push_relabel(graph, source, target)
                        optimization_results = f"Max flow from {source} to {target}: {flow}"
                        logging.debug(f"Completed Push-Relabel algorithm with flow: {flow}")
                    
                    pa = ' '
                    pa += str(path[0])
                    for p in path[1:]:
                        pa += ' ---> ' + str(p)
                             
                except Exception as e:
                    # Catch any exceptions from the algorithms
                    error_message = f"An error occurred while running the optimization: {str(e)}"
                    logging.error(f"An error occurred: {e}")

    context = {
        'form': form,
        'optimization_results': optimization_results,
        'error_message': error_message,
        'best_algorithm': best_algorithm,
        'path': pa,
    }
    
    return render(request, 'optimization_page.html', context)

# views.py

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.models import User

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        
        
        # Send email
        subject = 'New Contact Form Submission'
        message_body = f"Name: {name}\nEmail: {email}\n\nMessage: {message}"
        sender_email = email  # Sender's email address
        receiver_email = ['shanjayathithya2004@gmail.com']  # Receiver's email address (can be a list)
        
        send_mail(subject, message_body, sender_email, receiver_email)
        
        # Redirect the user to a thank you page after submitting the form
        return HttpResponseRedirect(reverse('thank_you'))  # Change 'thank_you' to your thank you page URL
        
    return render(request, 'contact_us.html')
