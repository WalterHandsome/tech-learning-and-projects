# RecyclerView 深入

## 1. Adapter 与 ViewHolder

```kotlin
class UserAdapter(
    private val onItemClick: (User) -> Unit
) : ListAdapter<User, UserAdapter.UserViewHolder>(UserDiffCallback()) {

    inner class UserViewHolder(
        private val binding: ItemUserBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(user: User) {
            binding.tvName.text = user.name
            binding.tvEmail.text = user.email
            binding.root.setOnClickListener { onItemClick(user) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return UserViewHolder(binding)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}
```

## 2. DiffUtil

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: User, newItem: User) = oldItem == newItem
}

// 使用 ListAdapter 自动处理差异更新
adapter.submitList(newList)
```

## 3. LayoutManager

```kotlin
// 线性布局
recyclerView.layoutManager = LinearLayoutManager(context)
recyclerView.layoutManager = LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)

// 网格布局
recyclerView.layoutManager = GridLayoutManager(context, 2).apply {
    spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
        override fun getSpanSize(position: Int) = if (position == 0) 2 else 1
    }
}

// 瀑布流
recyclerView.layoutManager = StaggeredGridLayoutManager(2, StaggeredGridLayoutManager.VERTICAL)

// ItemDecoration
recyclerView.addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))
```

## 4. 多类型列表

```kotlin
sealed class ListItem {
    data class Header(val title: String) : ListItem()
    data class Content(val user: User) : ListItem()
}

class MultiTypeAdapter : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {
    override fun getItemViewType(position: Int) = when (getItem(position)) {
        is ListItem.Header -> TYPE_HEADER
        is ListItem.Content -> TYPE_CONTENT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        TYPE_HEADER -> HeaderViewHolder(ItemHeaderBinding.inflate(/*..*/))
        else -> ContentViewHolder(ItemContentBinding.inflate(/*..*/))
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = getItem(position)) {
            is ListItem.Header -> (holder as HeaderViewHolder).bind(item)
            is ListItem.Content -> (holder as ContentViewHolder).bind(item)
        }
    }

    companion object { const val TYPE_HEADER = 0; const val TYPE_CONTENT = 1 }
}
```

## 5. Paging3

```kotlin
// PagingSource
class UserPagingSource(private val api: ApiService) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        val page = params.key ?: 1
        return try {
            val response = api.getUsers(page, params.loadSize)
            LoadResult.Page(
                data = response.data,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.data.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, User>) =
        state.anchorPosition?.let { state.closestPageToPosition(it)?.prevKey?.plus(1) }
}

// ViewModel
class UserViewModel(private val api: ApiService) : ViewModel() {
    val users: Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5)
    ) { UserPagingSource(api) }.flow.cachedIn(viewModelScope)
}

// Activity / Compose
val lazyPagingItems = viewModel.users.collectAsLazyPagingItems()
LazyColumn {
    items(lazyPagingItems.itemCount) { index ->
        lazyPagingItems[index]?.let { UserCard(it) }
    }
}
```
