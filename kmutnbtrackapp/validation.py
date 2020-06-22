from django.contrib.auth.password_validation import *
from django.utils.translation import gettext as _, ngettext


class CustomMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "รหัสผ่านของุคุณสั้นเกินไป คุณต้องกำหนดรหัสผ่านของคุณอย่างน้อย %(min_length)d ตัวอักษร",
                    "รหัสผ่านของุคุณสั้นเกินไป คุณต้องกำหนดรหัสผ่านของคุณอย่างน้อย %(min_length)d ตัวอักษร",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "รหัสผ่านของคุณต้องมีอย่างน้อย %(min_length)d ตัวอักษร",
            "รหัสผ่านของคุณต้องมีอย่างน้อย %(min_length)d ตัวอักษร",
            self.min_length
        ) % {'min_length': self.min_length}


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("รหัสผ่านของคุณคล้ายกับ %(verbose_name)s เกินไป"),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

    def get_help_text(self):
        return _('รหัสผ่านของคุณต้องไม่ใกล้เคียงกับข้อมูลอย่างอื่นมากเกินไป')


class CustomCommonPasswordValidator(CommonPasswordValidator):
    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("รหัสผ่านของคุณคาดเดาง่ายเกินไป"),
                code='password_too_common',
            )

    def get_help_text(self):
        return _('รหัสผ่านของคุณต้องไม่คาดเดาง่ายเกินไป')


class CustomNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("รหัสผ่านของคุณมีแต่ตัวเลข"),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _('รหัสผ่านของคุณต้องไม่มีแต่ตัวเลข')
