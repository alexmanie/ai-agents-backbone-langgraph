import gradio as gr


class UIUtils:
    """
    Utility class for managing UI utils.
    """
    @staticmethod
    def accumulate_totals(last_call, total) -> int:
        """
        Toggle the visibility state of a UI component.

        Parameters:
            total: The current total value.
            last_call: The value to be added to the total.

        Returns:
            int: The updated total value.
        """

        if total is None:
            total = 0

        new_total = int(total) + int(last_call)
        return new_total
