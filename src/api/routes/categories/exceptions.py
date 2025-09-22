from fastapi import HTTPException, status


CategoryNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Category not found"
)


