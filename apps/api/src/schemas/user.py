subscription = relationship(
    "Subscription",
    uselist=False,
    back_populates="user",
)