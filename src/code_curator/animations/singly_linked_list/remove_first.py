from __future__ import annotations


from data_structures.nodes.singly_linked_list_node import SLLNode

from ..data_structure_animation import PackageAnimation
from .data_structure_animator import assign_subanimations_and_animate
from .data_structure_animator import BaseSLLPackager
from .subanimations.center_sll import CenterSLL
from .subanimations.empty import Empty
from .subanimations.fade_out_container import FadeOutContainer
from .subanimations.fade_out_mobject import FadeOutMobject
from .subanimations.move_trav import MoveTrav

# class _RemoveFirst(Animation):
#     def __init__(
#         self,
#         sll,
#         node:      SLLNode,
#         pointer_to_next,
#         mob_anims: dict,
#         run_time:  int = 1,
#         rate_func = linear,
#         **kwargs
#     ):
#         run_time = len(mob_anims)
#         super().__init__(
#             sll,
#             run_time=run_time,
#             rate_func=rate_func,
#             **kwargs
#         )
#         self.sll = sll
#         self.node = node
#         self.container = self.node.container
#         self.pointer_to_next = pointer_to_next
#         self.head = self.sll._head
#         self.head_pointer = self.sll.head_pointer
#         self.mob_groups = mob_anims
#         self.num_animations = len(self.mob_groups)
#         self.alpha_thresholds = {num: num / self.num_animations for num in self.mob_groups}
#         self.alpha_step_size = 1 / self.num_animations

#     def begin(self) -> None:
#         self.sll.save_state()
#         self.pointer_to_next.save_state()
#         self.head_pointer.save_state()

#         self.original_sll_location = self.sll.get_center()
#         self.original_left = self.sll.get_left()
#         super().begin()

#     def interpolate_mobject(self, alpha: float) -> None:
#         for animation_num, mob_group in self.mob_groups.items():
#             for mob_name, mob in mob_group.items():
#                 normalized_alpha = self._get_normalized_alpha(alpha, animation_num)

#                 if normalized_alpha <= 0 or normalized_alpha >= 1:
#                     continue

#                 if mob_name == 'container':
#                     mob.set_stroke(opacity=1 - normalized_alpha)
#                     for container_sub in mob.submobjects:
#                         container_sub.set_opacity(1 - normalized_alpha)
#                 elif mob_name == 'pointer_to_next':
#                     mob.set_opacity(1 - normalized_alpha)
#                 elif mob_name == 'head_pointer':
#                     mob.restore()
#                     mob.move_immediately_alpha(self.head, self.head, smooth(normalized_alpha))
#                 elif mob_name == 'sll':
#                     mob.move_to([0, 0, 0])
#                     mob.shift(LEFT * smooth(normalized_alpha))

#     def clean_up_from_scene(self, scene: Scene = None) -> None:
#         # scene.add(self.node)
#         scene.remove(self.node)
#         self.sll.remove(self.node)
#         # self.node.remove(self.sll)
#         super().clean_up_from_scene(scene)

#     def _get_normalized_alpha(self, alpha: float, animation_num: int) -> float:
#         start_alpha = self.alpha_thresholds[animation_num] - self.alpha_step_size
#         end_alpha = start_alpha + self.alpha_step_size

#         if alpha < start_alpha:
#             return 0
#         elif start_alpha <= alpha <= end_alpha:
#             alpha = (alpha - (self.alpha_step_size * (animation_num - 1))) / self.alpha_step_size
#             if alpha > 1:
#                 alpha = 1
#             return alpha
#         elif alpha > end_alpha:
#             return 1
#         else:
#             raise Exception(f'Animation number {animation_num} has alpha {alpha}')

#     def _get_mob_animation_num(self, mob_name: str) -> int:
#         for animation_num, mob_group in self.mob_groups.items():
#             if mob_name in mob_group:
#                 return animation_num
#         raise


class RemoveFirst(BaseSLLPackager):
    def __init__(self, sll):
        self._sll = sll

        # self._fade_in_container = Empty(self._sll)
        self._fade_out_container = Empty(self._sll)
        self._fade_out_pointer = Empty(self._sll)
        # self._pointer_animation = Empty(self._sll)
        self._move_trav = Empty(self._sll)
        self._center_sll = Empty(self._sll)

        # self._node = None
        # self._pointer_to_next = None
        # self._mob_anims = None

    def _set_kwargs_defaults(self, **kwargs) -> dict:
        return kwargs

    def _assign_subanimations(self, index: int, node: SLLNode):
        # self._fade_in_container = FadeInContainer(self._sll, node.container)
        self._fade_out_container = FadeOutContainer(
            self._sll, node.container, node,
        )
        self._fade_out_pointer = FadeOutMobject(
            self._sll, node.pointer_to_next, node,
        )
        # self._pointer_animation = self._get_pointer_animation(node, pointer_animation_type)
        self._move_trav = MoveTrav(
            self._sll, self._sll.head_pointer, self._sll._head,
        )
        self._center_sll = CenterSLL(
            self._sll, curr_reference_index=0, post_subanimation_reference_index=1,
        )

    @assign_subanimations_and_animate
    def all_together(self, *args, **kwargs) -> PackageAnimation:
        self.append_concurrent_animations(
            self._fade_out_container,
            self._fade_out_pointer,
            self._move_trav,
            self._center_sll,
        )
        # self.append_concurrent_animations(
        # )

    # def _remove_node_and_animate(fn):
    #     def inner(self, *args, **kwargs):
    #         self._node = self._remove_node(*args, **kwargs)
    #         fn(self, *args, **kwargs)
    #         return self._create_animation()
    #     return inner

    #################
    # One animation #
    #################
    # @_remove_node_and_animate
    # def all_together(self) -> Animation:
    #     self._mob_anims = {
    #         1: {
    #             'container': self._node._container,
    #             'pointer_to_next': self._node._pointer_to_next,
    #             'head_pointer': self._sll.head_pointer,
    #             'sll': self._sll
    #         }
    #     }

    # def _remove_node(self) -> None:
    #     removed_node = self._sll._head
    #     self._pointer_to_next = self._sll._head.pointer_to_next
    #     del self._sll._nodes[0]

    #     self._sll._head = self._sll[0]
    #     return removed_node

    # def _create_animation(self):
    #     if self._node is None or self._mob_anims is None:
    #         raise RuntimeError('Make node or mob_anims has not been set yet!')

    #     return _RemoveFirst(
    #         sll=self._sll,
    #         node=self._node,
    #         pointer_to_next=self._pointer_to_next,
    #         mob_anims=self._mob_anims
    #     )
