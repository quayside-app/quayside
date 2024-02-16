from django import forms

from api.models import Task


class NewProjectForm(forms.Form):
    description = forms.CharField(label="What is your project about?",
                                  widget=forms.TextInput(attrs={
                                      "placeholder": "I want to bake a cake!",
                                      "class": "w-96 block mt-3 text-sm rounded-md mt-1 p-2 bg-neutral-600 outline-none placeholder-gray-400",
                                      "type": "text",
                                  })
                                  )


class TaskForm(forms.Form):
    # Can't use forms.ModelForm bc it's mongo
    name = forms.CharField(label="Name",
                           widget=forms.TextInput(attrs={
                               "type": "text",
                           })
                           )

    description = forms.CharField(label="Description",
                                  widget=forms.TextInput(attrs={
                                      "type": "text",
                                  })
                                  )
