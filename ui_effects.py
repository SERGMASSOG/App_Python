from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, Qt, QSize, QRect)
from PySide6.QtWidgets import QStackedWidget, QFrame, QPushButton

class UIEffects:
    @staticmethod
    def setup_stack_transition(stack_widget: QStackedWidget, duration=300):
        """Configura transiciones suaves para un QStackedWidget"""
        stack_widget.setTransitionDirection(Qt.Horizontal)
        stack_widget.setTransitionSpeed(duration)
        stack_widget.setTransitionEasingCurve(QEasingCurve.OutExpo)
        stack_widget.setSlideTransition(True)

    @staticmethod
    def create_hover_card(card: QFrame, hover_color="#2D3748"):
        """Aplica efecto hover a una tarjeta"""
        # Guardar el estilo original
        original_style = card.styleSheet()
        
        def enter_event(event):
            animation = QPropertyAnimation(card, b"windowOpacity")
            animation.setDuration(200)
            animation.setStartValue(card.windowOpacity())
            animation.setEndValue(0.95)
            animation.start()
            
            # Sutil elevación y sombra
            card.setStyleSheet(f"""
                {original_style}
                QFrame {{
                    background-color: {hover_color};
                    border: 1px solid #4A5568;
                    border-radius: 8px;
                }}
            """)
        
        def leave_event(event):
            animation = QPropertyAnimation(card, b"windowOpacity")
            animation.setDuration(200)
            animation.setStartValue(card.windowOpacity())
            animation.setEndValue(1.0)
            animation.start()
            card.setStyleSheet(original_style)
        
        card.enterEvent = enter_event
        card.leaveEvent = leave_event

    @staticmethod
    def create_hover_button(button: QPushButton, hover_color="#2D3748"):
        """Aplica efecto hover a un botón"""
        original_style = button.styleSheet()
        
        def enter_event(event):
            button.setStyleSheet(f"""
                {original_style}
                QPushButton {{
                    background-color: {hover_color};
                    padding: 8px 16px;
                    border-radius: 4px;
                    border: 1px solid #4A5568;
                }}
                QPushButton:hover {{
                    background-color: #3c4b64;
                }}
            """)
        
        def leave_event(event):
            button.setStyleSheet(original_style)
        
        button.enterEvent = enter_event
        button.leaveEvent = leave_event
