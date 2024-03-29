from __future__ import annotations

import inspect
import itertools as it
from typing import TYPE_CHECKING

import numpy as np
from manim import VMobject
from manim.utils.family_ops import restructure_list_to_exclude_certain_family_members

from code_curator.custom_logging.custom_logger import CustomLogger
from code_curator.null_vmobject import NullVMobject

if TYPE_CHECKING:
    from manim.typing import Point3D_Array


logger = CustomLogger.getLogger(__name__)


class CustomVMobject(VMobject):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.quasi_mobjects: list[VMobject] = []

    def add(self, *mobjects: VMobject) -> None:
        non_null_vmobjects: list[VMobject] = []
        for mob in mobjects:
            if mob is None:
                raise TypeError(
                    f"Can't add NoneType to submobjects: {mobjects}",
                )

            if isinstance(mob, VMobject) and not isinstance(mob, NullVMobject):
                non_null_vmobjects.append(mob)

        super().add(*non_null_vmobjects)

    def quasi_add(self, *mobjects: VMobject) -> None:
        """Add each mobject in ``mobjects`` to ``self`` such that they don't contribute to boundary.

        A mobject will be added to ``self.submobjects`` and will move with ``self``. It will not however,
        contribute to the points that define the boundary of ``self``. This is seen with labels on vertices.
        Regardless of where the label is relative to the rest of the vertex, the vertex will be positioned as
        if the label is not part of the mobject, with the label maintaing the same relative distance. This can
        be thought of as just adding an updater to the label such that it follows the vertex. That solution, as
        far as I know, is too cumbersome to achieve as it would require making the scene an attribute of vertex,
        which leads to issues when making copies of mobjects.

        Args:
            mobjects: The VMobjects to be added in a quasi manner
        """
        self.add(*mobjects)
        self.quasi_mobjects.extend(mobjects)

    def get_points_defining_boundary(self) -> Point3D_Array:
        """Exclude quasi_mobjects from defining boundary.

        .. seealso:: :meth:`~custom_vmobject.CustomVMobject.quasi_add`
        """
        return np.array(
            tuple(
                it.chain(
                    *(
                        sm.get_anchors()
                        for sm in restructure_list_to_exclude_certain_family_members(
                            self.get_family(),
                            to_remove=self.quasi_mobjects,
                        )
                    ),
                ),
            ),
        )

    def force_update(self, recursive: bool = True):
        family = self.get_family()
        is_suspended_list = [mob.updating_suspended for mob in family]
        self.resume_updating()

        for index, mob in enumerate(family):
            if is_suspended_list[index]:
                mob.suspend_updating(recursive=False)

        return self

    def update(self, dt: float = 0, recursive: bool = True):
        if not self.updating_suspended:
            for updater in self.updaters:
                if "dt" in inspect.signature(updater).parameters:
                    updater(self, dt)
                else:
                    updater(self)

        if recursive:
            for submob in self.submobjects:
                submob.update(dt, recursive)

        return self
