from django import forms


class NewProjectForm(forms.Form):
    """
    A form for creating a new project with a description.
    """

    description = forms.CharField(
        label="What is your project about?",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bake a cake",
                "class": "w-72 md:w-96 block mt-3 p-2 text-sm rounded-md bg-neutral-600 outline-none placeholder-gray-400",
                "type": "text",
            }
        ),
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
                'rows': 1,
            }
        ),
    )

    status = forms.ChoiceField(
        label="",
        required=False,
        choices=(("Todo", "Todo"), ("In-Progress",
                 "In-Progress"), ("Done", "Done")),
        widget=forms.Select(
            attrs={
                "class": "text-xs md:text-base inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
            }
        ),
    )

    startDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "text-xs md:text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )

    endDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "text-xs md:text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
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
    
    durationDays = forms.IntegerField(
        label="Days",
        required=False,
        widget=forms.Select(
            choices=[(x,x) for x in range(0, 11)],
            attrs={
                "class": "text-xs md:text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400"
            }
        ),
    )
    
    durationHours = forms.IntegerField(
        label="Hours",
        required=False,
        widget=forms.Select(
			choices=[(x,x) for x in range(1, 24)],
            attrs={
                "class": "text-xs md:text-base inline-block pl-1 py-1  rounded-md  bg-neutral-600 outline-none placeholder-gray-400"
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
                'rows': 1,
            }
        ),
    )

    startDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )

    endDate = forms.DateField(
        label="",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "inline-block p-1 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                "type": "date",
            }
        ),
    )