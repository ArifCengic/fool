from django import forms

class CommentForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea(attrs={'rows': 4, 'cols': 80}), max_length=200)
