from django import forms

from api.models import Task


class NewProjectForm(forms.Form):
    description = forms.CharField(label="What is your project about?",
                                  widget=forms.TextInput(attrs={
                                      "placeholder": "I want to bake a cake!",
                                      "class": "w-96 block mt-3 p-2 text-sm rounded-md   bg-neutral-600 outline-none placeholder-gray-400",
                                      "type": "text",
                                  })
                                  )


class TaskForm(forms.Form):
    # Can't use forms.ModelForm bc it's mongo
    name = forms.CharField(label="",
                           widget=forms.TextInput(attrs={
                               "type": "text",
                               "class": "w-full block bg-neutral-800 outline-none sm:text-2xl font-bold",
                           })
                           )

    description = forms.CharField(label="",
                                  required=False,
                                  widget=forms.Textarea(attrs={
                                      "placeholder": "Description...",
                                      "type": "text",
                                      "class": "w-full block p-2 mt-4 rounded-md  bg-neutral-600 outline-none placeholder-gray-400",
                                  })
                                  )
