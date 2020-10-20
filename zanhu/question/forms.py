from django import forms

from zanhu.question.models import Question

from markdownx.fields import MarkdownxFormField


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())  # 隐藏
    content = MarkdownxFormField()

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "status"]
