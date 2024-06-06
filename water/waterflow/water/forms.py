from django import forms
from .models import NetworkComponent, Edge, Node


class NetworkComponentForm(forms.ModelForm):
    class Meta:
        model = NetworkComponent
        fields = ['name', 'component_type', 'description']
        
class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ['name', 'type', 'latitude', 'longitude']
        widgets = {
            'type': forms.Select(choices=Node.NODE_TYPE_CHOICES),
        }

class EdgeForm(forms.ModelForm):
    class Meta:
        model = Edge
        fields = ['source', 'target', 'flow_rate']

        # Custom labels (if you want to customize the labels of the form fields)
        labels = {
            'source': 'Source Node',
            'target': 'Target Node',
            'flow_rate': 'Flow Rate',
        }

        # Help texts (if you want to provide any help texts for the form fields)
        help_texts = {
            'source': 'Select the source node from the list.',
            'target': 'Select the target node from the list.',
            'flow_rate': 'Enter the flow rate for the edge.',
        }

    # Custom validation to ensure that source and target nodes are not the same
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        target = cleaned_data.get('target')

        # Ensure the source and target nodes are not the same
        if source.type == 'outlet':
            raise forms.ValidationError('Outlet cannot be selected.')
        
        if target.type == 'tank':
            raise forms.ValidationError('Tank (source) cannot be a internal node')
        
        if source == target:
            raise forms.ValidationError('Source and target nodes cannot be the same.')

        return cleaned_data

class OptimizationForm(forms.Form):
    # Choices for optimization algorithms
    algorithm_choices = [
        #('dijkstra', 'Dijkstra'),
        ('edmonds_karp', 'Edmonds-Karp'),
        ('ford_fulkerson', 'Ford-Fulkerson'),
        ('dinic', 'Dinic'),
        ('push_relabel', 'Push-Relabel')
        #('simplex', 'Simplex')
    ]
    
    # Form fields
    algorithm = forms.ChoiceField(choices=algorithm_choices, label="Optimization Algorithm")
    source_node = forms.ModelChoiceField(
        queryset=Node.objects.all(),
        label="Source Node",
        required=True
    )
    target_node = forms.ModelChoiceField(
        queryset=Node.objects.all(),
        label="Target Node",
        required=True
    )
    
    
    
    # Clean method to validate the form data
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source_node')
        target = cleaned_data.get('target_node')

        # Check if the source and target nodes are the same
        if source.type != 'tank':
            raise forms.ValidationError("The source should be a Tank")
        if target.type == 'tank' or target.type == 'valve':
            raise forms.ValidationError("The target must me an outlet")
        if source == target:
            raise forms.ValidationError(
                "Source and Target nodes cannot be the same."
            )

        return cleaned_data
