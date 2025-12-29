import requests
from django.conf import settings
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service unifié pour gérer les notifications via Telegram et Twilio"""
    
    def __init__(self):
        # Configuration Twilio
        self.twilio_client = None
        if self._has_twilio_config():
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                logger.warning(f"Twilio non configuré: {e}")
    
    def _has_twilio_config(self):
        """Vérifie si Twilio est configuré"""
        return all([
            hasattr(settings, 'TWILIO_ACCOUNT_SID'),
            hasattr(settings, 'TWILIO_AUTH_TOKEN'),
            hasattr(settings, 'TWILIO_PHONE_NUMBER'),
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER,
        ])
    
    def send_telegram(self, text: str) -> bool:
        """Envoie un message Telegram via l'API officielle. Retourne True si OK."""
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            r = requests.post(url, data={"chat_id": chat_id, "text": text})
            return r.ok
        except Exception:
            return False
    
    def send_voice_call(self, to_number: str, message: str, priority: str = 'critical') -> dict:
        """
        Envoie un appel vocal via Twilio
        
        Args:
            to_number (str): Numéro à appeler (format: +212XXXXXXXXX)
            message (str): Message à lire
            priority (str): 'low', 'medium', 'high', 'critical'
        
        Returns:
            dict: {'success': bool, 'call_sid': str, 'error': str}
        """
        if not self.twilio_client:
            logger.error("Twilio non configuré")
            return {
                'success': False,
                'error': 'Twilio non configuré'
            }
        
        try:
            # Message d'intro selon la priorité
            intro = self._get_intro_by_priority(priority)
            
            # TwiML avec voix française
            twiml = f'''
            <Response>
                <Say language="fr-FR" voice="Polly.Celine">
                    {intro}
                    {message}
                    Je répète.
                    {message}
                    Fin du message. Au revoir.
                </Say>
            </Response>
            '''
            
            # Lancer l'appel
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                twiml=twiml,
                timeout=30,
                record=False
            )
            
            logger.info(f"Appel vocal envoyé: {call.sid} vers {to_number}")
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'appel: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_temperature_alert(self, temp: float, dt, phone_number: str = None) -> dict:
        """
        Envoie une alerte de température via tous les canaux configurés
        
        Args:
            temp (float): Température détectée
            dt: Date/heure de la mesure
            phone_number (str): Numéro pour l'appel vocal (optionnel)
        
        Returns:
            dict: Résultats pour chaque canal
        """
        results = {
            'telegram': {'success': False},
            'voice_call': {'success': False, 'enabled': bool(phone_number)}
        }
        
        # Message pour Telegram
        telegram_msg = (
            f"⚠️ Alerte Température Critique!\n\n"
            f"🌡️ Température: {temp:.1f} °C (Seuil: 25°C)\n"
            f"📅 Date/Heure: {dt}\n"
            f"👥 Groupe B: Imane Bouchlaghem et Sara Tsouli\n\n"
            f"⚡ Action requise immédiatement!"
        )
        
        # Message pour appel vocal
        voice_msg = (
            f"Alerte critique. "
            f"La température du réfrigérateur a atteint {temp:.1f} degrés Celsius. "
            f"Cette situation est critique pour la chaîne du froid. "
            f"Une intervention immédiate est requise."
        )
        
        # Envoyer via Telegram
        try:
            results['telegram']['success'] = self.send_telegram(telegram_msg)
            if results['telegram']['success']:
                logger.info(f"Alerte Telegram envoyée pour temp={temp}°C")
        except Exception as e:
            results['telegram']['error'] = str(e)
            logger.error(f"Erreur Telegram: {e}")
        
        # Envoyer appel vocal si numéro fourni
        if phone_number:
            try:
                voice_result = self.send_voice_call(
                    to_number=phone_number,
                    message=voice_msg,
                    priority='critical'
                )
                results['voice_call'].update(voice_result)
                if voice_result['success']:
                    logger.info(f"Appel vocal envoyé pour temp={temp}°C vers {phone_number}")
            except Exception as e:
                results['voice_call']['error'] = str(e)
                logger.error(f"Erreur appel vocal: {e}")
        
        return results
    
    def _get_intro_by_priority(self, priority: str) -> str:
        """Retourne l'introduction selon la priorité"""
        intros = {
            'low': "Bonjour, vous avez une nouvelle alerte de priorité faible.",
            'medium': "Bonjour, vous avez une alerte importante.",
            'high': "Attention! Vous avez une alerte de priorité élevée.",
            'critical': "ALERTE CRITIQUE! Attention, ceci est une alerte critique nécessitant votre attention immédiate."
        }
        return intros.get(priority, intros['critical'])


# Instance globale
notification_service = NotificationService()


# Fonctions de compatibilité avec l'ancien code
def send_telegram(text: str) -> bool:
    """Fonction legacy pour compatibilité"""
    return notification_service.send_telegram(text)


def appel_alerte_temperature(temp: float, date, numero: str = None) -> str:
    """
    Fonction legacy pour compatibilité
    
    Args:
        temp (float): Température
        date: Date/heure
        numero (str): Numéro de téléphone (optionnel)
    
    Returns:
        str: Call SID si succès, None sinon
    """
    # Si aucun numéro fourni, utiliser celui des settings si disponible
    if not numero and hasattr(settings, 'ALERT_PHONE_NUMBER'):
        numero = settings.ALERT_PHONE_NUMBER
    
    if numero:
        result = notification_service.send_temperature_alert(
            temp=temp,
            dt=date,
            phone_number=numero
        )
        
        if result['voice_call'].get('success'):
            return result['voice_call']['call_sid']
    
    return None