from django import forms
from datetime import datetime, timezone

class NewProjectForm(forms.Form):
    """
    A form for creating a new project with a name and description.
    """

    name = forms.CharField(
        label="What is your project called?",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Operation bake a cake",
                "class": "w-72 md:w-96 block mt-2 mb-4 p-2  text-sm rounded-md bg-neutral-600 outline-none placeholder-gray-400",
                "type": "text",
            }
        ),
    )

    description = forms.CharField(
        label="Describe your project:",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "I want to bake a chocolate cake for my friend's birthday party.",
                "class": "w-72 md:w-96 block mt-2 mb-2 p-2 text-sm rounded-md bg-neutral-600 outline-none placeholder-gray-400",
                "rows": 4,
            }
        ),
    )


class TaskFeedbackForm(forms.Form):
    userID = forms.CharField(widget=forms.HiddenInput())  # Assuming the user ID is handled in the background
    projectID = forms.CharField(widget=forms.HiddenInput())  # Assuming the project ID is handled in the background
    taskID = forms.CharField(required=False, widget=forms.HiddenInput())  # Optional, can be null
    dateCreated = forms.DateTimeField(initial=datetime.now(timezone.utc), widget=forms.HiddenInput())  # Default to current time
    mood = forms.ChoiceField(
        choices=(
            (1, "Very Unhappy"),
            (2, "Unhappy"),
            (3, "Neutral"),
            (4, "Happy"),
            (5, "Very Happy")
        ),
        label="How are you feeling about things?",
        widget=forms.Select(attrs={
            "class": "block w-full mt-2 p-2 rounded-md bg-neutral-600 outline-none"
        })
    )
    explanation = forms.CharField(
        label="Can you explain why you feel this way?",
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "I feel this way because...",
            "class": "w-full block mt-2 mb-4 p-2 text-sm rounded-md bg-neutral-600 outline-none placeholder-gray-400",
            "rows": 3,
        })
    )




class TaskForm(forms.Form):
    """
    A form for creating a new task with a name and description.
    """

    # Can't use forms.ModelForm bc it's mongo
    name = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Name",
                "type": "text",
                "class": "w-full block bg-neutral-800 outline-none sm:text-2xl font-bold",
                "rows": 1,
            }
        ),
    )

    status = forms.ChoiceField(
        label="",
        required=False,
        choices=(("Todo", "Todo"), ("In-Progress", "In-Progress"), ("Done", "Done")),
        widget=forms.Select(
            attrs={
                "class": "text-base inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
            }
        ),
    )

    startDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )

    endDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )

    description = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Description...",
                "type": "text",
                "class": "w-full block p-2 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
            }
        ),
    )
    
    duration = forms.CharField(
        required=False,
        max_length=18, # Mongo can handle a max of 8 bytes (~18 digits)
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ex: 4h 30m",
                "type": "text",
                "class": " inline-block bg-neutral-800 outline-none font-bold placeholder-gray-400",
                'rows': 1,
            }
        ),
    )


class ProjectForm(forms.Form):
    """
    A form for editing a task with a name.
    """

    # Can't use forms.ModelForm bc it's mongo
    name = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Project Name",
                "type": "text",
                "class": "w-full block bg-neutral-800 outline-none sm:text-2xl font-bold",
                "rows": 1,
            }
        ),
    )

    startDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": " text-base inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )

    endDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "text-base inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )
    contributors = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Contributor Emails",
                "type": "text",
                "class": "w-full p-2  rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "rows": 2,
            }
        ),
    )
