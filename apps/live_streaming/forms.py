from django import forms
from .models import LiveStream


class LiveStreamStartForm(forms.ModelForm):
    class Meta:
        model = LiveStream
        fields = ['title', 'description', 'playback_url', 'ingest_url', 'stream_key']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'stream_key': forms.PasswordInput(render_value=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['playback_url'].required = False
        self.fields['ingest_url'].required = False
        self.fields['stream_key'].required = False
        self.fields['playback_url'].help_text = 'Optional: Leave empty if using Agora (auto-configured)'
        self.fields['ingest_url'].help_text = 'Optional: For AWS IVS or custom streaming'
        self.fields['stream_key'].help_text = 'Optional: Keep secret if using external provider'

    def clean_playback_url(self):
        playback_url = self.cleaned_data.get('playback_url', '').strip()
        if playback_url and not playback_url.startswith('https://'):
            raise forms.ValidationError('Playback URL must start with https:// for security.')
        return playback_url

    def clean_ingest_url(self):
        ingest_url = self.cleaned_data.get('ingest_url', '').strip()
        if ingest_url and not ingest_url.startswith('https://'):
            raise forms.ValidationError('Ingest URL must start with https:// for security.')
        return ingest_url
