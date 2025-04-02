import gettext as original_gettext
import re
import logging

def mark_for_translation(message: str) -> str:
    """
    Wraps the target string literal for translation but does NOT return the translated string.
    This is used to mark strings for extraction by translation tools.
    """
    return message

class TranslationVariableMissingError(Exception):
    """
    Raised when a translation does not include the expected named variable(s).

    e.g. source string: "Hello, {name}!" but the translation is "Bonjour!" or
    "Bonjour, {}!" instead of "Bonjour, {name}!"
    """
    def __init__(self, locale=None, message=None, translated=None, expected_vars=None):
        self.locale = locale
        self.message = message
        self.translated = translated
        self.expected_vars = expected_vars

    def __str__(self):
        if self.expected_vars and self.message and self.translated:
            return (f"Translation error in locale '{self.locale}': "
                   f"Missing or incorrect variable formatting.\n"
                   f"Expected variables: {', '.join([f'{{{var}}}' for var in self.expected_vars])}\n"
                   f"Original: '{self.message}'\n"
                   f"Translation: '{self.translated}'")
        return f"Translation error in locale '{self.locale}'"

def seedsigner_gettext(message: str, **kwargs):
    """
    Enhanced gettext with built-in variable formatting and better error messages.
    
    Args:
        message: The message to translate
        **kwargs: Variables to substitute in the translated message
        
    Returns:
        Translated and formatted string
        
    Raises:
        TranslationVariableMissingError: When translation has missing or incorrect variables
    """
    # Get the translated message
    translated = original_gettext.gettext(message)
    
    # If no kwargs, no formatting needed
    if not kwargs:
        return translated
    
    try:
        # Try to format with the provided kwargs
        return translated.format(**kwargs)
    except (KeyError, IndexError, ValueError) as e:
        # Import here to avoid circular import issues
        from seedsigner.models.settings import Settings
        from seedsigner.models.settings_definition import SettingsConstants
        
        try:
            locale = Settings.get_instance().get_value(SettingsConstants.SETTING__LOCALE)
        except:
            locale = "unknown"
        
        # Create detailed error message
        if isinstance(e, IndexError) and re.search(r'{}', translated):
            # Empty {} brackets instead of named variables
            logging.error(f"Translation contains empty brackets {{}} instead of named variables in locale '{locale}'")
        elif isinstance(e, KeyError):
            # Missing named variable
            missing_var = str(e).strip("'")
            logging.error(f"Translation missing named variable {{{missing_var}}} in locale '{locale}'")
        else:
            # Other formatting error
            logging.error(f"Translation formatting error in locale '{locale}': {str(e)}")
        
        # Raise custom exception with helpful details
        raise TranslationVariableMissingError(
            locale=locale,
            message=message,
            translated=translated,
            expected_vars=list(kwargs.keys())
        ) from e

def seedsigner_ngettext(singular: str, plural: str, n: int, **kwargs):
    """
    Enhanced ngettext with built-in variable formatting and better error messages.
    Handles plural forms based on the value of n.
    
    Args:
        singular: The singular form message
        plural: The plural form message
        n: The count that determines which form to use
        **kwargs: Variables to substitute in the translated message
        
    Returns:
        Translated and formatted string
        
    Raises:
        TranslationVariableMissingError: When translation has missing or incorrect variables
    """
    # Get the translated message
    translated = original_gettext.ngettext(singular, plural, n)
    
    # If no kwargs, no formatting needed
    if not kwargs:
        return translated
    
    try:
        # Try to format with the provided kwargs
        return translated.format(**kwargs)
    except (KeyError, IndexError, ValueError) as e:
        # Import here to avoid circular import issues
        from seedsigner.models.settings import Settings
        from seedsigner.models.settings_definition import SettingsConstants
        
        try:
            locale = Settings.get_instance().get_value(SettingsConstants.SETTING__LOCALE)
        except:
            locale = "unknown"
        
        # Source message (either singular or plural based on n)
        source_msg = singular if n == 1 else plural
        
        # Raise custom exception with helpful details
        raise TranslationVariableMissingError(
            locale=locale,
            message=source_msg,
            translated=translated,
            expected_vars=list(kwargs.keys())
        ) from e