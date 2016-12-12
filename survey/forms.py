from django import forms

from .models import Survey


class SurveyForm(forms.Form):

    survey = forms.ChoiceField(
        choices=[[survey.survey_name, survey.survey_name] for survey in Survey.objects.all().order_by('survey_name')],
        label="Survey ",
        initial=None,
        help_text="")

    def cleaned_data(self):
        raise forms.ValidationError('This form cannot be edited. See app_configuration instead.')
        cleaned_data = self.cleaned_data
        return cleaned_data

    class Meta:
        model = Survey
        fields = '__all__'
