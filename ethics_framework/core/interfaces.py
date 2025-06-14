"""
ethics_framework/core/interfaces.py
===================================
Formal interface specifications for layer communication
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Protocol, runtime_checkable, Tuple
from abc import ABC, abstractmethod
import time


@dataclass
class Decision:
    """Represents a decision request in the system"""
    user_id: int
    content_id: int
    algorithm: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'user_id': self.user_id,
            'content_id': self.content_id,
            'algorithm': self.algorithm,
            'attributes': self.attributes,
            'timestamp': self.timestamp
        }


@dataclass
class LayerInterface:
    """
    Formal specification of interface between layers
    Implements interface theory for compositional verification
    """
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    preconditions: List[str]
    postconditions: List[str]
    invariants: List[str]
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input against schema"""
        # Simplified schema validation
        for key, schema in self.input_schema.items():
            if key not in data:
                return False
            # Type checking would go here
        return True
    
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate output against schema"""
        for key, schema in self.output_schema.items():
            if key not in data:
                return False
            # Type checking would go here
        return True


@dataclass
class LayerMetrics:
    """Performance metrics for a layer"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    last_update: float = field(default_factory=time.time)
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


@runtime_checkable
class EthicalProcessor(Protocol):
    """Protocol for ethical processing components"""
    
    def validate(self, decision: Decision, context: Dict[str, Any]) -> bool:
        """Validate decision against ethical constraints"""
        ...
    
    def process(self, decision: Decision) -> Dict[str, Any]:
        """Process decision with ethical considerations"""
        ...


class InterfaceComposition:
    """
    Manages composition of layer interfaces
    Ensures compositional correctness
    """
    
    def __init__(self):
        self.interfaces: Dict[Tuple[int, int], LayerInterface] = {}
        
    def register_interface(self, from_layer: int, to_layer: int, 
                          interface: LayerInterface):
        """Register interface between layers"""
        self.interfaces[(from_layer, to_layer)] = interface
        
    def validate_composition(self) -> Tuple[bool, List[str]]:
        """
        Validate that all interfaces compose correctly
        Returns (is_valid, error_messages)
        """
        errors = []
        
        # Check interface compatibility
        for (from_layer, to_layer), interface in self.interfaces.items():
            # Check if output of from_layer matches input of to_layer
            if (from_layer - 1, from_layer) in self.interfaces:
                prev_interface = self.interfaces[(from_layer - 1, from_layer)]
                
                # Verify schema compatibility
                for key in interface.input_schema:
                    if key not in prev_interface.output_schema:
                        errors.append(
                            f"Missing required input '{key}' in interface "
                            f"from layer {from_layer} to {to_layer}"
                        )
                
                # Verify postconditions -> preconditions
                for precond in interface.preconditions:
                    if precond not in prev_interface.postconditions:
                        errors.append(
                            f"Precondition '{precond}' not satisfied by "
                            f"layer {from_layer} postconditions"
                        )
        
        return len(errors) == 0, errors
    
    def get_pipeline_specification(self) -> Dict[str, Any]:
        """Get complete pipeline specification"""
        return {
            'interfaces': {
                f"L{fl}_to_L{tl}": {
                    'input': interface.input_schema,
                    'output': interface.output_schema,
                    'preconditions': interface.preconditions,
                    'postconditions': interface.postconditions,
                    'invariants': interface.invariants
                }
                for (fl, tl), interface in self.interfaces.items()
            },
            'composition_valid': self.validate_composition()[0]
        }


class MessageBus:
    """
    Message bus for inter-layer communication
    Provides decoupling and monitoring capabilities
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.max_history_size = 10000
        
    def subscribe(self, topic: str, callback: callable):
        """Subscribe to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        
    def publish(self, topic: str, message: Dict[str, Any]):
        """Publish message to a topic"""
        # Record in history
        self.message_history.append({
            'topic': topic,
            'message': message,
            'timestamp': time.time()
        })
        
        # Trim history if needed
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
        
        # Notify subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    callback(message)
                except Exception as e:
                    # Log error but continue notifying others
                    print(f"Error in message bus callback: {e}")
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get message statistics"""
        topic_counts = {}
        for entry in self.message_history:
            topic = entry['topic']
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            'total_messages': len(self.message_history),
            'topics': topic_counts,
            'subscribers_per_topic': {
                topic: len(subs) for topic, subs in self.subscribers.items()
            }
        }


class FeedbackLoop:
    """
    Implements feedback loop from Layer 5 to Layer 1
    Enables adaptive learning
    """
    
    def __init__(self):
        self.feedback_buffer: List[Dict[str, Any]] = []
        self.processed_feedback = 0
        self.adaptation_history = []
        
    def submit_feedback(self, feedback: Dict[str, Any]):
        """Submit feedback from governance layer"""
        self.feedback_buffer.append({
            'feedback': feedback,
            'timestamp': time.time(),
            'processed': False
        })
        
    def process_feedback_batch(self, batch_size: int = 100) -> Dict[str, Any]:
        """Process a batch of feedback"""
        # Get unprocessed feedback
        unprocessed = [f for f in self.feedback_buffer if not f['processed']]
        batch = unprocessed[:batch_size]
        
        if not batch:
            return {'processed_count': 0, 'adaptations': []}
        
        # Analyze feedback
        adaptations = self._analyze_feedback(batch)
        
        # Mark as processed
        for feedback_entry in batch:
            feedback_entry['processed'] = True
        
        self.processed_feedback += len(batch)
        
        # Record adaptation
        adaptation_record = {
            'timestamp': time.time(),
            'feedback_count': len(batch),
            'adaptations': adaptations
        }
        self.adaptation_history.append(adaptation_record)
        
        return {
            'processed_count': len(batch),
            'adaptations': adaptations
        }
    
    def _analyze_feedback(self, feedback_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze feedback and generate adaptations"""
        adaptations = []
        
        # Analyze constraint violations
        violation_counts = {}
        for entry in feedback_batch:
            feedback = entry['feedback']
            for violation in feedback.get('violations', []):
                constraint = violation.get('constraint_name')
                violation_counts[constraint] = violation_counts.get(constraint, 0) + 1
        
        # Generate adaptations for frequently violated constraints
        threshold = len(feedback_batch) * 0.1  # 10% threshold
        for constraint, count in violation_counts.items():
            if count > threshold:
                adaptations.append({
                    'type': 'constraint_weight_adjustment',
                    'constraint': constraint,
                    'action': 'increase_weight',
                    'reason': f'High violation rate: {count}/{len(feedback_batch)}'
                })
        
        return adaptations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get feedback loop statistics"""
        return {
            'total_feedback': len(self.feedback_buffer),
            'processed_feedback': self.processed_feedback,
            'pending_feedback': len([f for f in self.feedback_buffer if not f['processed']]),
            'total_adaptations': sum(len(a['adaptations']) for a in self.adaptation_history),
            'recent_adaptations': self.adaptation_history[-10:] if self.adaptation_history else []
        }


class SystemOrchestrator:
    """
    Orchestrates the complete five-layer system
    Manages layer lifecycle and communication
    """
    
    def __init__(self):
        self.layers: Dict[int, Any] = {}  # Layer instances
        self.interfaces = InterfaceComposition()
        self.message_bus = MessageBus()
        self.feedback_loop = FeedbackLoop()
        self.is_running = False
        
    def register_layer(self, layer_id: int, layer_instance: Any):
        """Register a layer in the system"""
        self.layers[layer_id] = layer_instance
        
        # Subscribe to layer output
        topic = f"layer_{layer_id}_output"
        self.message_bus.subscribe(topic, 
                                 lambda msg: self._handle_layer_output(layer_id, msg))
        
    def register_interface(self, from_layer: int, to_layer: int, 
                          interface: LayerInterface):
        """Register interface between layers"""
        self.interfaces.register_interface(from_layer, to_layer, interface)
        
    def validate_system(self) -> Tuple[bool, List[str]]:
        """Validate complete system configuration"""
        errors = []
        
        # Check all layers are registered
        for i in range(1, 6):
            if i not in self.layers:
                errors.append(f"Layer {i} not registered")
        
        # Validate interface composition
        interface_valid, interface_errors = self.interfaces.validate_composition()
        errors.extend(interface_errors)
        
        return len(errors) == 0, errors
    
    def process_decision(self, decision: Decision, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a decision through the complete pipeline
        """
        if not self.is_running:
            raise RuntimeError("System not started")
        
        context = context or {}
        current_data = {
            'decision': decision.to_dict(),
            'context': context,
            'pipeline_start_time': time.time()
        }
        
        # Process through each layer
        for layer_id in range(1, 6):
            if layer_id not in self.layers:
                raise RuntimeError(f"Layer {layer_id} not available")
            
            layer = self.layers[layer_id]
            
            try:
                # Process in layer
                layer_output = layer.process(current_data)
                
                # Publish output
                self.message_bus.publish(f"layer_{layer_id}_output", layer_output)
                
                # Prepare input for next layer
                current_data = layer_output
                
            except Exception as e:
                # Handle layer failure
                error_msg = f"Error in layer {layer_id}: {str(e)}"
                self.message_bus.publish("layer_error", {
                    'layer_id': layer_id,
                    'error': str(e),
                    'decision': decision.to_dict()
                })
                raise RuntimeError(error_msg)
        
        # Process feedback if governance layer produced any
        if 'governance_decision' in current_data:
            if not current_data['governance_decision']['approved']:
                self.feedback_loop.submit_feedback({
                    'decision': decision.to_dict(),
                    'violations': current_data['governance_decision'].get('policy_violations', []),
                    'timestamp': time.time()
                })
        
        # Add pipeline metadata
        current_data['pipeline_metadata'] = {
            'total_time_ms': (time.time() - current_data['pipeline_start_time']) * 1000,
            'layers_processed': 5,
            'message_bus_stats': self.message_bus.get_message_stats()
        }
        
        return current_data
    
    def start(self):
        """Start the system"""
        valid, errors = self.validate_system()
        if not valid:
            raise RuntimeError(f"System validation failed: {errors}")
        
        self.is_running = True
        
    def stop(self):
        """Stop the system"""
        self.is_running = False
        
    def _handle_layer_output(self, layer_id: int, output: Dict[str, Any]):
        """Handle output from a layer"""
        # Could implement cross-layer monitoring here
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        return {
            'is_running': self.is_running,
            'layers': {
                layer_id: {
                    'name': layer.name,
                    'metrics': {
                        'total_requests': layer.metrics.total_requests,
                        'success_rate': layer.metrics.success_rate(),
                        'avg_processing_time_ms': layer.metrics.average_processing_time * 1000
                    }
                }
                for layer_id, layer in self.layers.items()
            },
            'message_bus': self.message_bus.get_message_stats(),
            'feedback_loop': self.feedback_loop.get_statistics(),
            'interfaces': self.interfaces.get_pipeline_specification()
        }