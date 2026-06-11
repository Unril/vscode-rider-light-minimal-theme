using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Examples;

/// <summary>Tracking attribute.</summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
sealed class TrackedAttribute(string label = "") : Attribute {
    public string Label { get; } = label;
}

enum Role {
    Admin,
    Editor,
    Viewer
}

interface IRepository<in TId, out T> {
    T? FindById(TId id);
    IEnumerable<T> FindAll();
}

delegate TResult Transform<in T, out TResult>(T arg);

record User(long Id, string Name, HashSet<Role> Roles) {
    public User(long id, string name) : this(id, name, []) {
    }

    public string DisplayName => $"{Name} (id={Id})";
}

record struct Point(double X, double Y);

readonly struct UserId(long value) {
    public long Value { get; } = value > 0
        ? value
        : throw new ArgumentOutOfRangeException(nameof(value));
}

[Tracked(label: "repository")]
class UserRepository : IRepository<UserId, User>, IDisposable {
    private readonly Dictionary<long, User> _store = new();
    private bool _disposed;

    public const string TableName = "users";
    public static readonly int MaxRetries = 3;
    public event EventHandler<User>? UserSaved;

    public User? FindById(UserId id) {
        return _store.GetValueOrDefault(id.Value);
    }

    public IEnumerable<User> FindAll() => _store.Values;

    public void Save(User user) {
        _store[user.Id] = user;
        UserSaved?.Invoke(this, user);
    }

    public void Dispose() {
        if (_disposed) return;
        _store.Clear();
        _disposed = true;
        GC.SuppressFinalize(this);
    }
}

static class UserExtensions {
    public static bool IsAdmin(this User user) => user.Roles.Contains(Role.Admin);
    public static IEnumerable<User> Admins(this IEnumerable<User> users) => users.Where(u => u.IsAdmin());
}

static class Showcase {
    static async Task<T> RetryAsync<T>(Func<int, Task<T>> block) {
        Exception? last = null;
        for (var i = 0; i < 3; i++) {
            try {
                return await block(i);
            } catch (Exception e) {
                last = e;
            }
        }

        throw last ?? new InvalidOperationException("failed");
    }

    static string PatternMatch(object? obj, List<User> users) {
        var kind = obj switch {
            User { Roles: var roles } u when roles.Contains(Role.Admin) => $"admin:{u.Name}",
            User u => $"user:{u.Name}",
            int i => $"int:{i}",
            null => "null",
            _ => "other"
        };

        var names = from u in users
            where u.Roles.Count > 0
            orderby u.Name
            select u.DisplayName;

        var admins = users.Admins().Select(u => u.Name).ToList();

        var hex = 0xFF;
        var fp = 3.14f + 1e5;
        var verbatim = @"multi\nline";
        var raw = """raw "string" literal""";
        var escape = "tab:\there\n";

        _ = obj is User { Id: > 0 } admin && admin.IsAdmin();
        return kind;
    }
}

class Matrix {
    private readonly double[,] _data;
    public Matrix(int rows, int cols) => _data = new double[rows, cols];

    public double this[int row, int col] {
        get => _data[row, col];
        set => _data[row, col] = value;
    }

    public static Matrix operator +(Matrix a, Matrix b) => a;
    public static implicit operator Matrix(double[,] d) => new(d.GetLength(0), d.GetLength(1));
}

#if DEBUG
static class DebugHelpers {
    public static void Log(string msg) => Console.WriteLine($"[DEBUG] {msg}");
}
#endif
