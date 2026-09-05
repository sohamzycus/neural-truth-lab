"""Manual floating-point bit representation for teaching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class FloatBits:
    format_name: str
    bits: str
    sign: int
    exponent_bits: str
    fraction_bits: str
    represented_value: float
    error: float


def _bits_to_str(n: int, width: int) -> str:
    return format(n, f"0{width}b")


def fp32_bits(value: float) -> FloatBits:
    import struct

    bits_int = struct.unpack("!I", struct.pack("!f", value))[0]
    sign = (bits_int >> 31) & 1
    exp = (bits_int >> 23) & 0xFF
    frac = bits_int & 0x7FFFFF
    bits = _bits_to_str(bits_int, 32)
    # decode
    if exp == 0 and frac == 0:
        decoded = 0.0 if sign == 0 else -0.0
    elif exp == 0xFF:
        decoded = float("nan") if frac else float("-inf" if sign else "inf")
    else:
        mant = 1.0 + frac / (2**23)
        decoded = ((-1) ** sign) * (2 ** (exp - 127)) * mant
    return FloatBits(
        format_name="FP32",
        bits=bits,
        sign=sign,
        exponent_bits=_bits_to_str(exp, 8),
        fraction_bits=_bits_to_str(frac, 23),
        represented_value=decoded,
        error=abs(decoded - value),
    )


def bf16_bits(value: float) -> FloatBits:
    import torch

    t = torch.tensor([value], dtype=torch.float32).to(torch.bfloat16)
    # recover bits from uint16
    u16 = t.view(torch.uint16).item()
    sign = (u16 >> 15) & 1
    exp = (u16 >> 7) & 0xFF
    frac = u16 & 0x7F
    bits = _bits_to_str(u16, 16)
    if exp == 0 and frac == 0:
        decoded = 0.0 if sign == 0 else -0.0
    elif exp == 0xFF:
        decoded = float("nan") if frac else float("-inf" if sign else "inf")
    else:
        mant = 1.0 + frac / (2**7)
        decoded = ((-1) ** sign) * (2 ** (exp - 127)) * mant
    return FloatBits(
        format_name="BF16",
        bits=bits,
        sign=sign,
        exponent_bits=_bits_to_str(exp, 8),
        fraction_bits=_bits_to_str(frac, 7),
        represented_value=decoded,
        error=abs(decoded - value),
    )


def fp8_e4m3_bits(value: float) -> FloatBits:
    """Encode/decode FP8 E4M3 (4 exponent, 3 mantissa, bias 7)."""
    import math

    if value == 0.0:
        return FloatBits("FP8 E4M3", "00000000", 0, "0000", "000", 0.0, abs(value))

    sign = 1 if value < 0 else 0
    x = abs(value)
    if math.isnan(x):
        return FloatBits("FP8 E4M3", "01111111", 0, "1111", "111", float("nan"), float("nan"))

    # Find exponent
    exp_unbiased = math.floor(math.log2(x))
    exp = exp_unbiased + 7
    if exp <= 0:
        # subnormal
        mant = x / (2 ** (1 - 7))
        frac = int(round(mant * 8)) & 0x7
        exp_bits = 0
        decoded = ((-1) ** sign) * (2 ** (1 - 7)) * (frac / 8.0)
    elif exp >= 15:
        exp_bits = 15
        frac = 0
        decoded = ((-1) ** sign) * float("inf")
    else:
        mant = x / (2 ** exp_unbiased) - 1.0
        frac = int(round(mant * 8)) & 0x7
        exp_bits = exp
        mantissa = 1.0 + frac / 8.0
        decoded = ((-1) ** sign) * (2 ** (exp_bits - 7)) * mantissa

    bits_int = (sign << 7) | (exp_bits << 3) | frac
    return FloatBits(
        format_name="FP8 E4M3",
        bits=_bits_to_str(bits_int, 8),
        sign=sign,
        exponent_bits=_bits_to_str(exp_bits, 4),
        fraction_bits=_bits_to_str(frac, 3),
        represented_value=decoded,
        error=abs(decoded - value) if not math.isinf(decoded) else float("inf"),
    )


def format_field_bits(row: FloatBits) -> str:
    """SIGN | EXPONENT | FRACTION layout for teaching."""
    return f"{row.sign} | {row.exponent_bits} | {row.fraction_bits}"


def format_precision_comparison_table() -> str:
    rows = represent_value(0.1)
    lines = [
        "| Property | FP32 | BF16 | FP8 E4M3 |",
        "| --- | --- | --- | --- |",
        f"| precision (error on 0.1) | {rows[0].error:.3e} | {rows[1].error:.3e} | {rows[2].error:.3e} |",
        "| range | very large | very large | smaller |",
        "| memory / value | 4 bytes | 2 bytes | 1 byte |",
        "| speed potential | baseline | higher on modern accelerators | highest when supported |",
        "| training stability | safest | usually fine | needs scaling/range care |",
    ]
    return "\n".join(lines)


def explain_why_not_exact(value: float = 0.1) -> str:
    return (
        f"Decimal {value} is a repeating fraction in base 2, "
        "like 1/3 is repeating in base 10. "
        "So the computer stores the nearest representable binary value, not the exact decimal."
    )


def represent_value(value: float) -> List[FloatBits]:
    return [fp32_bits(value), bf16_bits(value), fp8_e4m3_bits(value)]


def format_table(value: float) -> str:
    rows = represent_value(value)
    lines = [
        "| Format | Bits | Represented value | Error |",
        "| --- | --- | ---: | ---: |",
    ]
    for r in rows:
        err = f"{r.error:.6g}" if r.error == r.error else "nan"
        lines.append(
            f"| {r.format_name} | `{r.bits}` | {r.represented_value:.10g} | {err} |"
        )
    return "\n".join(lines)
