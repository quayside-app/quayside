from django import forms


class NewProjectForm(forms.Form):
    description = forms.CharField(label="What is your project about?",
                                  widget=forms.TextInput(attrs={
                                        "placeholder": "I want to bake a cake!",
                                      "class": "w-96 block mt-3 text-sm rounded-md mt-1 p-2 bg-neutral-600 outline-none placeholder-gray-400",
                                      "type": "text",
                                  })
                                  )
