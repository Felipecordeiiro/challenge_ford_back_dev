from fastapi import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse

class DecodeTokenException(HTTPException):
    """Decodificação do token"""
    def __init__(self, e):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na decodificação do token: {str(e)}"
        )
    pass

class EncodingTokenException(HTTPException):
    """Codificação do token"""
    def __init__(self, e):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na codificação do token: {str(e)}"
        )
    pass

class RefreshTokenException(HTTPException):
    """O usuário não forneceu um refresh token válido"""
    def __init__(self, e):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token de atualização inválido: {str(e)}"
        )
    pass

class TokenExpiredException(HTTPException):
    """Usuário forneceu um token expirado"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

class TokenNotFoundException(HTTPException):
    """Token não se encontra no banco de dados"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token não encontrado no banco de dados",
        )

class InvalidTokenException(HTTPException):
    """Usuário forneceu um token inválido"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    pass

class InvalidCredentials(HTTPException):
    """Usuário forneceu um credenciais (email, senha) inválidas"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    pass

class InsufficientPermission(HTTPException):
    """User does not have the neccessary permissions to perform an action."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permissões insuficientes para chamar essa rota. Por favor se autentique e tente novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    pass

class UserAlreadyExists(HTTPException):
    """User has provided an email for a user who exists during sign up."""

    pass

class UserNotFound(HTTPException):
    """Usuário não encontrado no banco de dados"""
    def __init__(self, user):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Usuário {user} não encontrado.",
        )

    pass

def configure_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )