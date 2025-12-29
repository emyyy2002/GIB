from .models import Dht11
from .serializer import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .utils import notification_service
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def Dlist(request):
    all_data = Dht11.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})


class Dhtviews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        instance = serializer.save()
        temp = instance.temp
        
        # Seuil de température (peut être configuré dans settings.py)
        temp_threshold = getattr(settings, 'TEMP_THRESHOLD', 8)
        temp_min = getattr(settings, 'TEMP_MIN', 2)

         # 🚨 Alerte seulement si température < 2 ou > 8
        if temp < temp_min or temp > temp_threshold:
            logger.warning(
                f"Température critique détectée: {temp}°C "
                f"(plage normale: {temp_min}-{temp_threshold}°C)"
            )
            # 1) Email (optionnel)
            if getattr(settings, 'SEND_EMAIL_ALERTS', True):
                try:
                    send_mail(
                        subject="⚠️ Alerte Température élevée",
                        message=(
                            f"Groupe B: Imane Bouchlaghem et Sara Tsouli\n\n"
                            f"La température a atteint {temp:.1f} °C à {instance.dt}.\n"
                            f"Seuil d'alerte: {temp_threshold}°C"
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=getattr(settings, 'ALERT_EMAIL_RECIPIENTS', ["osm.saidi@gmail.com"]),
                        fail_silently=True,
                    )
                    logger.info("Email d'alerte envoyé")
                except Exception as e:
                    logger.error(f"Erreur envoi email: {e}")

            # 2) Notifications Telegram + Appel vocal via le service unifié
            phone_number = getattr(settings, 'ALERT_PHONE_NUMBER', None)
            
            results = notification_service.send_temperature_alert(
                temp=temp,
                dt=instance.dt,
                phone_number=phone_number
            )
            
            # Logger les résultats
            if results['telegram']['success']:
                logger.info("✅ Alerte Telegram envoyée avec succès")
            else:
                logger.error(f"❌ Échec Telegram: {results['telegram'].get('error', 'Unknown')}")
            
            if results['voice_call']['enabled']:
                if results['voice_call']['success']:
                    logger.info(f"✅ Appel vocal envoyé: {results['voice_call'].get('call_sid')}")
                else:
                    logger.error(f"❌ Échec appel vocal: {results['voice_call'].get('error', 'Unknown')}")
            
            # Retourner les résultats dans la réponse (optionnel)
            self.notification_results = results
        
        return instance
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Ajouter les résultats des notifications dans la réponse
        if hasattr(self, 'notification_results'):
            response.data['notifications'] = self.notification_results
        
        return response