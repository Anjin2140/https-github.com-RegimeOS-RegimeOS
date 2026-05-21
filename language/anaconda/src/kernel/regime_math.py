# Transpiled by ANACONDA Forge v1.0
import sys
if r'C:\RegimeOS\language\anaconda' not in sys.path:
    sys.path.insert(0, r'C:\RegimeOS\language\anaconda')

# Verify execution authorization
if __name__ == "__anaconda_secure__":
    try:
        from src.compiler.vault import verify_air_signature
        if not verify_air_signature(__file__):
            print("EXIT_CODE_SECURITY_VIOLATION")
            sys.exit(99)
    except Exception:
        print("EXIT_CODE_SECURITY_VIOLATION")
        sys.exit(99)

import os
import sys
import math
import inspect
import threading

class Ternary:

    def __init__(self, value: int):
        if value < -1:
            self.value = -1
        elif value > 1:
            self.value = 1
        else:
            self.value = int(value)

    def __and__(self, other):
        if self.value == 1 and other.value == -1 or (self.value == -1 and other.value == 1):
            return Ternary(0)
        return Ternary(min(self.value, other.value))

    def __or__(self, other):
        return Ternary(max(self.value, other.value))

    def __invert__(self):
        return Ternary(-self.value)

    def __xor__(self, other):
        if self.value == 0 or other.value == 0:
            return Ternary(0)
        return Ternary(-1 if self.value == other.value else 1)

    def __eq__(self, other):
        if isinstance(other, Ternary):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        if self.value == 1:
            return 'TRUE'
        elif self.value == -1:
            return 'FALSE'
        return 'UNKNOWN'

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return self.value == 1
Ternary.FALSE = Ternary(-1)
Ternary.UNKNOWN = Ternary(0)
Ternary.TRUE = Ternary(1)

class EpsilonStallDetector:
    _iteration_counts = threading.local()
    _last_values = threading.local()

    @classmethod
    def check_stall(cls, current_value, key, threshold=1000) -> Ternary:
        if not hasattr(cls._iteration_counts, 'dict'):
            cls._iteration_counts.dict = {}
        if not hasattr(cls._last_values, 'dict'):
            cls._last_values.dict = {}
        counts = cls._iteration_counts.dict
        vals = cls._last_values.dict
        if key not in counts:
            counts[key] = 1
            vals[key] = current_value
            return Ternary(0)
        last_val = vals[key]
        if last_val == current_value:
            counts[key] += 1
            if counts[key] > threshold:
                print(f'[!] WARN_EPSILON_STALL: Loop stall detected at {key}. Forcing resolution to TRUE.')
                return Ternary(1)
        else:
            counts[key] = 1
            vals[key] = current_value
        return Ternary(0)

    @classmethod
    def reset(cls, key):
        if hasattr(cls._iteration_counts, 'dict') and key in cls._iteration_counts.dict:
            del cls._iteration_counts.dict[key]
            del cls._last_values.dict[key]

class RegimeDecimal:
    BASE = 65536

    def __init__(self, sign: int, exponent: int, chunks: list[int]):
        self.sign = 0 if sign == 0 else -1 if sign < 0 else 1
        self.exponent = 0 if self.sign == 0 else exponent
        raw_chunks = chunks if chunks else []
        if self.sign == 0:
            self.chunks = []
        else:
            leading_zeros = 0
            while leading_zeros < len(raw_chunks) and raw_chunks[leading_zeros] == 0:
                leading_zeros += 1
            trailing_zeros = 0
            while trailing_zeros < len(raw_chunks) - leading_zeros and raw_chunks[-1 - trailing_zeros] == 0:
                trailing_zeros += 1
            new_len = len(raw_chunks) - leading_zeros - trailing_zeros
            if new_len <= 0:
                self.sign = 0
                self.exponent = 0
                self.chunks = []
            else:
                self.chunks = raw_chunks[leading_zeros:len(raw_chunks) - trailing_zeros]
                self.exponent -= leading_zeros

    @classmethod
    def from_float(cls, value: float):
        if value == 0.0:
            return cls(0, 0, [])
        sign = -1 if value < 0 else 1
        abs_val = abs(value)
        exp = int(math.floor(math.log(abs_val) / math.log(cls.BASE)))
        scale = abs_val / cls.BASE ** exp
        chunks = []
        for _ in range(8):
            digit = int(math.floor(scale))
            chunks.append(digit)
            scale = (scale - digit) * cls.BASE
            if scale == 0:
                break
        return cls(sign, exp, chunks)

    @classmethod
    def from_str(cls, s: str):
        s = s.strip()
        if not s or s == '0' or s == '0.0':
            return cls(0, 0, [])
        sign = 1
        if s.startswith('-'):
            sign = -1
            s = s[1:]
        elif s.startswith('+'):
            s = s[1:]
        if '.' in s:
            parts = s.split('.')
            int_str = parts[0]
            frac_str = parts[1]
        else:
            int_str = s
            frac_str = ''
        int_part = int(int_str) if int_str else 0
        frac_part = int(frac_str) if frac_str else 0
        frac_divisor = 10 ** len(frac_str) if frac_str else 1
        num = int_part * frac_divisor + frac_part
        den = frac_divisor
        if num == 0:
            return cls(0, 0, [])
        exp = 0
        while num < den:
            num *= cls.BASE
            exp -= 1
        while num >= den * cls.BASE:
            den *= cls.BASE
            exp += 1
        chunks = []
        for _ in range(20):
            digit = num // den
            chunks.append(digit)
            num = num % den * cls.BASE
            if num == 0:
                break
        return cls(sign, exp, chunks)

    def to_float(self) -> float:
        if self.sign == 0:
            return 0.0
        val = 0.0
        for i, chunk in enumerate(self.chunks):
            val += chunk * self.BASE ** (self.exponent - i)
        return self.sign * val

    def __str__(self):
        if self.sign == 0:
            return '0.0'
        num = 0
        for chunk in self.chunks:
            num = num * self.BASE + chunk
        scale_power = self.exponent - len(self.chunks) + 1
        if scale_power >= 0:
            final_val = num * self.BASE ** scale_power
            return ('-' if self.sign < 0 else '') + str(final_val) + '.0'
        else:
            den = self.BASE ** (-scale_power)
            int_part = num // den
            rem = num % den
            dec_frac = ''
            for _ in range(25):
                rem *= 10
                d = rem // den
                dec_frac += str(d)
                rem %= den
                if rem == 0:
                    break
            return ('-' if self.sign < 0 else '') + str(int_part) + '.' + (dec_frac if dec_frac else '0')

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if self.sign == 0:
            return other
        if other.sign == 0:
            return self
        if self.sign != other.sign:
            return self - RegimeDecimal(-other.sign, other.exponent, other.chunks)
        min_exp = min(self.exponent - len(self.chunks), other.exponent - len(other.chunks))
        a_offset = self.exponent - (len(self.chunks) - 1) - min_exp
        b_offset = other.exponent - (len(other.chunks) - 1) - min_exp
        length = max(self.exponent, other.exponent) - min_exp + 2
        result_chunks = [0] * length
        carry = 0
        for i in range(length):
            a_idx = len(self.chunks) - 1 - i + a_offset
            b_idx = len(other.chunks) - 1 - i + b_offset
            a_digit = self.chunks[a_idx] if 0 <= a_idx < len(self.chunks) else 0
            b_digit = other.chunks[b_idx] if 0 <= b_idx < len(other.chunks) else 0
            s = a_digit + b_digit + carry
            result_chunks[length - 1 - i] = s % self.BASE
            carry = s // self.BASE
        final_exp = max(self.exponent, other.exponent) + 1
        return RegimeDecimal(self.sign, final_exp, result_chunks)

    def __sub__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if other.sign == 0:
            return self
        if self.sign == 0:
            return RegimeDecimal(-other.sign, other.exponent, other.chunks)
        if self.sign != other.sign:
            return self + RegimeDecimal(-other.sign, other.exponent, other.chunks)
        cmp = self._compare_abs(other)
        if cmp == 0:
            return RegimeDecimal(0, 0, [])
        larger = self if cmp > 0 else other
        smaller = other if cmp > 0 else self
        min_exp = min(larger.exponent - len(larger.chunks), smaller.exponent - len(smaller.chunks))
        l_offset = larger.exponent - (len(larger.chunks) - 1) - min_exp
        s_offset = smaller.exponent - (len(smaller.chunks) - 1) - min_exp
        length = larger.exponent - min_exp + 1
        result_chunks = [0] * length
        borrow = 0
        for i in range(length):
            l_idx = len(larger.chunks) - 1 - i + l_offset
            s_idx = len(smaller.chunks) - 1 - i + s_offset
            l_digit = larger.chunks[l_idx] if 0 <= l_idx < len(larger.chunks) else 0
            s_digit = smaller.chunks[s_idx] if 0 <= s_idx < len(smaller.chunks) else 0
            diff = l_digit - s_digit - borrow
            if diff < 0:
                diff += self.BASE
                borrow = 1
            else:
                borrow = 0
            result_chunks[length - 1 - i] = diff
        final_sign = self.sign if cmp > 0 else -self.sign
        return RegimeDecimal(final_sign, larger.exponent, result_chunks)

    def __mul__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if self.sign == 0 or other.sign == 0:
            return RegimeDecimal(0, 0, [])
        len_a = len(self.chunks)
        len_b = len(other.chunks)
        temp = [0] * (len_a + len_b)
        for i in range(len_a):
            for j in range(len_b):
                temp[i + j + 1] += self.chunks[i] * other.chunks[j]
        result_chunks = [0] * len(temp)
        carry = 0
        for i in range(len(temp) - 1, -1, -1):
            val = temp[i] + carry
            result_chunks[i] = val % self.BASE
            carry = val // self.BASE
        final_exp = self.exponent + other.exponent + 1
        final_sign = self.sign * other.sign
        return RegimeDecimal(final_sign, final_exp, result_chunks)

    def __truediv__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if other.sign == 0:
            raise ZeroDivisionError('RegimeDecimal division by zero')
        if self.sign == 0:
            return RegimeDecimal(0, 0, [])
        num = 0
        for chunk in self.chunks:
            num = num * self.BASE + chunk
        den = 0
        for chunk in other.chunks:
            den = den * self.BASE + chunk
        exp = self.exponent - other.exponent
        while num < den:
            num *= self.BASE
            exp -= 1
        while num >= den * self.BASE:
            den *= self.BASE
            exp += 1
        chunks = []
        for _ in range(16):
            digit = num // den
            chunks.append(digit)
            num = num % den * self.BASE
            if num == 0:
                break
        return RegimeDecimal(self.sign * other.sign, exp, chunks)

    def _compare_abs(self, other) -> int:
        if self.exponent != other.exponent:
            return 1 if self.exponent > other.exponent else -1
        max_len = max(len(self.chunks), len(other.chunks))
        for i in range(max_len):
            a_digit = self.chunks[i] if i < len(self.chunks) else 0
            b_digit = other.chunks[i] if i < len(other.chunks) else 0
            if a_digit != b_digit:
                return 1 if a_digit > b_digit else -1
        return 0

    def __eq__(self, other):
        if not isinstance(other, RegimeDecimal):
            return False
        if self.sign != other.sign:
            return False
        if self.sign == 0:
            return True
        return self.exponent == other.exponent and self.chunks == other.chunks

    def __gt__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if self.sign != other.sign:
            return self.sign > other.sign
        if self.sign == 0:
            return False
        cmp = self._compare_abs(other)
        return cmp > 0 if self.sign > 0 else cmp < 0

    def __lt__(self, other):
        if not isinstance(other, RegimeDecimal):
            return NotImplemented
        if self.sign != other.sign:
            return self.sign < other.sign
        if self.sign == 0:
            return False
        cmp = self._compare_abs(other)
        return cmp < 0 if self.sign > 0 else cmp > 0

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

class HahnDecimal:

    def __init__(self, real: RegimeDecimal, eps_coeff: int=0):
        self.real = real
        self.eps_coeff = int(eps_coeff)

    def __add__(self, other):
        if isinstance(other, HahnDecimal):
            return HahnDecimal(self.real + other.real, self.eps_coeff + other.eps_coeff)
        return HahnDecimal(self.real + other, self.eps_coeff)

    def __sub__(self, other):
        if isinstance(other, HahnDecimal):
            return HahnDecimal(self.real - other.real, self.eps_coeff - other.eps_coeff)
        return HahnDecimal(self.real - other, self.eps_coeff)

    def __mul__(self, other):
        if isinstance(other, HahnDecimal):
            real = self.real * other.real
            eps = self.real.to_float() * other.eps_coeff + other.real.to_float() * self.eps_coeff
            return HahnDecimal(real, int(round(eps)))
        real = self.real * other
        eps = other.to_float() * self.eps_coeff
        return HahnDecimal(real, int(round(eps)))

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if isinstance(other, HahnDecimal):
            return HahnDecimal(other.real - self.real, other.eps_coeff - self.eps_coeff)
        return HahnDecimal(other - self.real, -self.eps_coeff)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __gt__(self, other) -> Ternary:
        key = self._get_caller_key()
        stall = EpsilonStallDetector.check_stall(self.real, key)
        if stall.value != 0:
            return stall
        if isinstance(other, HahnDecimal):
            if self.real > other.real:
                return Ternary(1)
            if self.real < other.real:
                return Ternary(-1)
            if self.eps_coeff > other.eps_coeff:
                return Ternary(1)
            if self.eps_coeff < other.eps_coeff:
                return Ternary(-1)
            return Ternary(0)
        if self.real > other:
            return Ternary(1)
        if self.real < other:
            return Ternary(-1)
        if self.eps_coeff > 0:
            return Ternary(1)
        if self.eps_coeff < 0:
            return Ternary(-1)
        return Ternary(0)

    def __lt__(self, other) -> Ternary:
        key = self._get_caller_key()
        stall = EpsilonStallDetector.check_stall(self.real, key)
        if stall.value != 0:
            return Ternary(-stall.value)
        if isinstance(other, HahnDecimal):
            if self.real < other.real:
                return Ternary(1)
            if self.real > other.real:
                return Ternary(-1)
            if self.eps_coeff < other.eps_coeff:
                return Ternary(1)
            if self.eps_coeff > other.eps_coeff:
                return Ternary(-1)
            return Ternary(0)
        if self.real < other:
            return Ternary(1)
        if self.real > other:
            return Ternary(-1)
        if self.eps_coeff < 0:
            return Ternary(1)
        if self.eps_coeff > 0:
            return Ternary(-1)
        return Ternary(0)

    def _get_caller_key(self) -> str:
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            if 'regime_math.py' not in filename and 'regime_math.ana' not in filename:
                return f'{filename}:{frame.f_lineno}'
            frame = frame.f_back
        return 'unknown_context'

    def __str__(self):
        if self.eps_coeff == 0:
            return str(self.real)
        return f'{self.real} + {self.eps_coeff}ε'

    def __repr__(self):
        return self.__str__()
RegimeDecimal.Zero = RegimeDecimal(0, 0, [])
RegimeDecimal.One = RegimeDecimal(1, 0, [1])
# SIGNATURE: 6992eead59d0ecae11f55239f8719355542e383b81beb5de144715dc66065d145195a728cbb0f1ae90f90f25f2116f3750138ef16faffc778a414aa32a9f3005
