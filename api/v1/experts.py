"""
Expert management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel

from api.v1.utils import get_chat_engine
from src.chat_engine import ChatEngine
from src.experts.factory import get_available_expert_types, get_expert_info
from src.common.logging import logger


# Create router
router = APIRouter(tags=["Experts"])


class ExpertSwitchRequest(BaseModel):
    """Request model for switching experts."""
    expert_type: str


class ExpertInfoResponse(BaseModel):
    """Response model for expert information."""
    current_expert: str
    expert_info: Dict[str, Any]
    available_experts: List[str]


class ExpertSwitchResponse(BaseModel):
    """Response model for expert switching."""
    success: bool
    message: str
    previous_expert: str
    current_expert: str


@router.get("/experts/current", response_model=ExpertInfoResponse)
async def get_current_expert_info(
    chat_engine: ChatEngine = Depends(get_chat_engine)
) -> ExpertInfoResponse:
    """
    Get information about the currently active expert.
    
    Returns:
        Information about the current expert and available options
    """
    try:
        current_expert_type = chat_engine.config.expert_type or "QNA"
        expert_info = chat_engine.get_current_expert_info()
        available_experts = get_available_expert_types()
        
        logger.info(f"Retrieved current expert info: {current_expert_type}")
        
        return ExpertInfoResponse(
            current_expert=current_expert_type,
            expert_info=expert_info,
            available_experts=available_experts
        )
    except Exception as e:
        logger.error(f"Error getting current expert info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert information: {str(e)}"
        )


@router.get("/experts/available")
async def get_available_experts() -> Dict[str, Any]:
    """
    Get information about all available expert types.
    
    Returns:
        Dictionary containing information about all available experts
    """
    try:
        available_experts = get_available_expert_types()
        expert_details = {}
        
        # Get detailed info for each expert type
        for expert_type in available_experts:
            try:
                expert_details[expert_type] = get_expert_info(expert_type)
            except Exception as e:
                logger.warning(f"Could not get info for expert type {expert_type}: {e}")
                expert_details[expert_type] = {
                    "name": f"{expert_type} Expert",
                    "description": f"Expert of type {expert_type}",
                    "capabilities": "Information not available"
                }
        
        logger.info(f"Retrieved information for {len(available_experts)} expert types")
        
        return {
            "available_experts": available_experts,
            "expert_details": expert_details,
            "total_count": len(available_experts)
        }
    except Exception as e:
        logger.error(f"Error getting available experts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available experts: {str(e)}"
        )


@router.post("/experts/switch", response_model=ExpertSwitchResponse)
async def switch_expert(
    request: ExpertSwitchRequest,
    chat_engine: ChatEngine = Depends(get_chat_engine)
) -> ExpertSwitchResponse:
    """
    Switch to a different expert type.
    
    Args:
        request: Request containing the new expert type
        
    Returns:
        Response indicating success or failure of the switch
    """
    try:
        previous_expert = chat_engine.config.expert_type or "QNA"
        new_expert_type = request.expert_type.upper()
        
        logger.info(f"Switching expert from {previous_expert} to {new_expert_type}")
        
        # Validate expert type
        available_experts = get_available_expert_types()
        if new_expert_type not in available_experts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid expert type: {new_expert_type}. Available types: {', '.join(available_experts)}"
            )
        
        # Perform the switch
        chat_engine.switch_expert(new_expert_type)
        
        logger.info(f"Successfully switched expert from {previous_expert} to {new_expert_type}")
        
        return ExpertSwitchResponse(
            success=True,
            message=f"Successfully switched from {previous_expert} to {new_expert_type}",
            previous_expert=previous_expert,
            current_expert=new_expert_type
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error switching expert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to switch expert: {str(e)}"
        )


@router.get("/experts/{expert_type}/info")
async def get_expert_type_info(expert_type: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific expert type.
    
    Args:
        expert_type: The type of expert to get information about
        
    Returns:
        Detailed information about the specified expert
    """
    try:
        expert_type_upper = expert_type.upper()
        available_experts = get_available_expert_types()
        
        if expert_type_upper not in available_experts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expert type not found: {expert_type}. Available types: {', '.join(available_experts)}"
            )
        
        expert_info = get_expert_info(expert_type_upper)
        
        logger.info(f"Retrieved info for expert type: {expert_type_upper}")
        
        return {
            "expert_type": expert_type_upper,
            "info": expert_info,
            "supported_operations": [
                "process_message",
                "stream_message", 
                "clear_history"
            ]
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting expert info for {expert_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert information: {str(e)}"
        ) 