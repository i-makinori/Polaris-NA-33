# Polaris-NA-33

BBS

## 到達

- 語りえないものについては、システム設計の段階では、考慮する必要はない。
- 匿名であっても、公開された場所で、議論したり、お喋りしたり、できる様にすること。
- 非哲学・哲学・形式検証・時空理論・数学・物理学・ソフトウェア・ハードウェア・などなどに、議題を限定するものではない。
- 各種の構想についても議論できる場とする。
- 個人

## 構成


Route構成。

| URL                               | 機能                                                                                                      |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| ./                                | 所謂 `index` ページ。 ToLopica の一覧、ToLopica の追加ページへのリンク。(Hot なトピックの提示。) 。その他色々...。              |
| ./index.html                      | `./` へのリダイレクト                                                                                       |
| ...                               | ...                                                                                                       |
| ./tolopica_add                    | ToLopica の追加ページ。                                                                                   |
| ./tolopica/<tolopica_name>?...... | ToLopica 内部のスレッド、投稿。 ?...... 以下はサーバまたはJavascriptへの命令の引数。                      |
| ...                               | ...                                                                                                       |
| ./ranference/<ranference_id>      | その id の RanFerence への直リンク。 ./tolopica/<tolopica_name>?id=<ranference_id> へのリダイレクト。     |
| ...                               | ...                                                                                                       |
| ./parambasis_pp                   | parambasis_pp/ 以下は管理者ページ。 管理者認証を必要とする。 基礎(則ちページでの法則)への介入を意味する。 |
| ./parambasis_pp/edit_index        | index のテンプレートの編集。                                                                              |
| ./parambasis_pp/edit_tolopica     | ToLopica の編集。                                                                                         |
| ./parambasis_pp/del_ranference    | RanFerence の削除。                                                                                       |
| ./parambasis_pp/edit_parapara     | 管理者の設定。                                                                                            |
| ...                               | ...                                                                                                       |
| ...                               | ...                                                                                                       |



## 用語集

| 用語          | 一般的な対応        | 語源・意味                                                        |
|---------------|---------------------|-------------------------------------------------------------------|
| Polaris-NA-33 | BBS-System          | 夢で聞いたことから。                                              |
| ToLopica      | 板(BB)              | Tropical Logical(?) Topica, Local Topic, equator ...              |
| RanFerence    | 投稿物(板へのPost)  | Random Radical ReFerenceable Inference.                           |
| -ropy         | 吸引作用            | ※ 用語の設定中                                                   |
| Parambasis    | 管理者ページ(Admin) | 希語の介入より。basisも入っていることから、baseへの介入ともなる。 |
| ...           |                     |                                                                   |



## 仕様

- 匿名掲示板システム。
- ユーザも板(ToLopica)の追加ができる。匿名のユーザであっても。
- 板への投稿物のPost(RanFerenceとしての投稿)も可能。匿名のユーザであっても。
- 表記
  - text 形式と markdown形式の選択が可能。
  - latex形式での数式表記ができる。
  - `>> <number>` により以前の投稿への引用ができる。 例えば、 `>> 101259` など。
- 投稿の前に確認もできること。
- ...
- 管理者による削除権限。削除履歴は残すこと。
- ユーザ機能(?)
- ...


## 実装指針

[documents/hints.md](documents/hints.md)




## install


```sh
$ # clone Repository to the directory
$ git clone https://github.com/i-makinori/Polaris-NA-33
$ #
$ cd host/
```

##### Make virtual environment if it is necsessary.

```sh
$ python3 -m venv .venv
$ # enable venv
$ source .venv/bin/activate # NOTE: maybe fail
```

##### install depends, and run server

```sh
$ pip install flask flask-sqlalchemy pyyaml
$ python route.py
```


