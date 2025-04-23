from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, engine, Base
import models, schemas, sentiment

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API RESTful d'Analyse de Sentiments",
    description="Analyse automatique des commentaires produits avec NLTK VADER.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

@app.post("/reviews", response_model=schemas.ReviewOut, status_code=201)
def add_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(id=review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    sentiment_score = sentiment.analyze_sentiment(review.comment_text)
    new_review = models.Review(
        product_id=review.product_id,
        user_name=review.user_name,
        comment_text=review.comment_text,
        timestamp=datetime.now(),
        sentiment_compound_score=sentiment_score
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@app.get("/reviews/product/{product_id}", response_model=list[schemas.ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return db.query(models.Review).filter_by(product_id=product_id).all()

@app.get("/products/{product_id}/sentiment_summary")
def sentiment_summary(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    reviews = db.query(models.Review).filter_by(product_id=product_id).all()
    total = len(reviews)
    if total == 0:
        return {"message": "Aucun commentaire pour ce produit"}

    positives = sum(1 for r in reviews if r.sentiment_compound_score >= 0.05)
    negatives = sum(1 for r in reviews if r.sentiment_compound_score <= -0.05)
    neutrals = total - positives - negatives
    avg_score = sum(r.sentiment_compound_score for r in reviews) / total

    return {
        "product_id": product.id,
        "product_name": product.name,
        "average_sentiment_score": avg_score,
        "positive_percentage": positives / total * 100,
        "negative_percentage": negatives / total * 100,
        "neutral_percentage": neutrals / total * 100,
        "total_reviews": total
    }