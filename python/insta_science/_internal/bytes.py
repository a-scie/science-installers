# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable


@dataclass(frozen=True)
class Unit:
    _name: str
    multiple: float
    _singular: str | None = None

    def render(self, total_bytes: int | float) -> str:
        return self._singular if (self._singular and round(total_bytes) == 1) else self._name


class ByteUnits(Unit, Enum):
    BYTES = "bytes", 1.0, "byte"
    KB = "kB", 1000 * BYTES[1]
    MB = "MB", 1000 * KB[1]
    GB = "GB", 1000 * MB[1]
    TB = "TB", 1000 * GB[1]
    PB = "PB", 1000 * TB[1]


@dataclass(frozen=True)
class ByteAmount(object):
    @classmethod
    def bytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.BYTES)

    @classmethod
    def kilobytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.KB)

    @classmethod
    def megabytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.MB)

    @classmethod
    def gigabytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.GB)

    @classmethod
    def terabytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.TB)

    @classmethod
    def petabytes(cls, total_bytes: int) -> ByteAmount:
        return cls(total_bytes=total_bytes, unit=ByteUnits.PB)

    @classmethod
    def human_readable(cls, total_bytes: int) -> ByteAmount:
        def select_unit():
            for unit in ByteUnits:
                if total_bytes < (1000 * unit.multiple):
                    return unit
            return ByteUnits.PB

        return cls(total_bytes=total_bytes, unit=select_unit())

    @classmethod
    def for_unit(cls, unit: Unit) -> Callable[[int], ByteAmount]:
        if ByteUnits.BYTES is unit:
            return cls.bytes
        elif ByteUnits.KB is unit:
            return cls.kilobytes
        elif ByteUnits.MB is unit:
            return cls.megabytes
        elif ByteUnits.GB is unit:
            return cls.gigabytes
        elif ByteUnits.TB is unit:
            return cls.terabytes
        elif ByteUnits.PB is unit:
            return cls.petabytes
        raise ValueError(
            "The unit {unit} has no known corresponding byte amount function".format(unit=unit)
        )

    total_bytes: int
    unit: Unit

    def __str__(self) -> str:
        amount = self.total_bytes / self.unit.multiple
        integer_part = math.trunc(amount)
        if self.unit is ByteUnits.BYTES or integer_part // 100 > 0:
            return "{amount} {unit}".format(amount=round(amount), unit=self.unit.render(amount))
        elif integer_part // 10 > 0:
            return "{amount:.1f} {unit}".format(amount=amount, unit=self.unit.render(amount))
        elif integer_part > 0:
            return "{amount:.2f} {unit}".format(amount=amount, unit=self.unit.render(amount))
        else:
            return "{amount:.3f} {unit}".format(amount=amount, unit=self.unit.render(amount))
