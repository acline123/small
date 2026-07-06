from app.models.database import Entity, Relation, get_db


def delete_graph_by_document(document_id: int):
    """删除指定文档的知识图谱数据。"""
    db = get_db()
    try:
        db.query(Relation).filter(Relation.document_id == document_id).delete()
        db.query(Entity).filter(Entity.document_id == document_id).delete()
        db.commit()
    finally:
        db.close()


def save_graph(document_id: int, entities: list[dict], relations: list[dict]) -> tuple[int, int]:
    """保存实体和关系到数据库，返回 (实体数, 关系数)。"""
    db = get_db()
    try:
        db.query(Relation).filter(Relation.document_id == document_id).delete()
        db.query(Entity).filter(Entity.document_id == document_id).delete()
        db.flush()

        name_to_id: dict[str, int] = {}
        for item in entities:
            name = (item.get("name") or "").strip()
            if not name or name in name_to_id:
                continue
            entity = Entity(
                name=name,
                entity_type=item.get("type", "概念"),
                document_id=document_id,
            )
            db.add(entity)
            db.flush()
            name_to_id[name] = entity.id

        relation_count = 0
        for item in relations:
            source = (item.get("source") or "").strip()
            target = (item.get("target") or "").strip()
            rel_type = (item.get("type") or "相关").strip()
            if not source or not target:
                continue
            if source not in name_to_id:
                entity = Entity(name=source, entity_type="概念", document_id=document_id)
                db.add(entity)
                db.flush()
                name_to_id[source] = entity.id
            if target not in name_to_id:
                entity = Entity(name=target, entity_type="概念", document_id=document_id)
                db.add(entity)
                db.flush()
                name_to_id[target] = entity.id
            db.add(
                Relation(
                    source_id=name_to_id[source],
                    target_id=name_to_id[target],
                    relation_type=rel_type,
                    document_id=document_id,
                )
            )
            relation_count += 1

        db.commit()
        return len(name_to_id), relation_count
    finally:
        db.close()
